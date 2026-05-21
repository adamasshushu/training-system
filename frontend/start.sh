#!/bin/bash
# ============================================
#  培训管理系统 — 前端启动脚本 (HTTPS)
# ============================================
#  使用方法:
#    bash start.sh              # 默认端口 5173
#    PORT=3000 bash start.sh    # 自定义端口
# ============================================
set -e
cd "$(dirname "$0")"

export PORT="${PORT:-5173}"
export BACKEND_PORT="${BACKEND_PORT:-8443}"

echo "🌐 培训管理系统前端 (HTTPS)"
echo "   地址: https://localhost:${PORT}"
echo "   后端: https://localhost:${BACKEND_PORT}"
echo ""

exec npx vite --host 0.0.0.0 --port "$PORT" --https
