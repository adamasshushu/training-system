#!/bin/bash
# ============================================
#  培训管理系统 — 生产环境启动脚本 (HTTPS)
# ============================================
#  使用方法:
#    bash start-prod.sh              # 默认端口 8443
#    PORT=9443 bash start-prod.sh    # 自定义端口
#    bash start-prod.sh --http       # HTTP 模式 (端口 8004)
# ============================================
set -e
cd "$(dirname "$0")"

# ---- 激活虚拟环境 ----
source ../venv/bin/activate

# ---- 配置 ----
export HOST="${HOST:-0.0.0.0}"
MODE="https"
PORT="8443"

if [[ "$1" == "--http" ]]; then
    MODE="http"
    PORT="${PORT:-8004}"
    echo "⚠️  HTTP 模式（仅开发环境）"
else
    PORT="${PORT:-8443}"
    if [[ ! -f cert.pem || ! -f key.pem ]]; then
        echo "🔐 生成自签名证书..."
        openssl req -x509 -newkey rsa:2048 -nodes \
            -keyout key.pem -out cert.pem -days 365 \
            -subj "/CN=localhost" 2>/dev/null
    fi
fi

# ---- 显示信息 ----
echo "🚀 培训管理系统 v2.2 (${MODE^^})"
echo "   数据库: $(python -c 'from app.config import settings; print(settings.DATABASE_URL)')"
echo "   地址: ${MODE}://${HOST}:${PORT}"
echo ""

# ---- 启动 ----
if [[ "$MODE" == "https" ]]; then
    exec python -m uvicorn app.main:app \
        --host "$HOST" --port "$PORT" \
        --ssl-keyfile key.pem --ssl-certfile cert.pem \
        --workers 2 --log-level warning --no-access-log
else
    exec python -m uvicorn app.main:app \
        --host "$HOST" --port "$PORT" \
        --workers 2 --log-level warning --no-access-log
fi
