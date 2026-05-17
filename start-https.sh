#!/bin/bash
# HTTPS启动脚本 - 用于局域网HTTPS访问
# 使用内置自签名证书

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
CERT_FILE="$BACKEND_DIR/cert.pem"
KEY_FILE="$BACKEND_DIR/key.pem"

echo "================================"
echo "  培训管理系统 - HTTPS启动"
echo "================================"
echo ""

# 检查证书
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "[!] 证书文件缺失，正在生成..."
    cd "$BACKEND_DIR"
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
      -days 3650 -nodes -subj '/CN=training-system/O=Internal/C=CN'
    echo "[✓] 自签名证书已生成"
fi

echo "[1/3] 启动后端API (HTTPS :8443)..."
cd "$BACKEND_DIR"
source ../venv/bin/activate
rm -f training.db

uvicorn app.main:app --host 0.0.0.0 --port 8443 \
  --ssl-certfile="$CERT_FILE" --ssl-keyfile="$KEY_FILE" &
BACKEND_PID=$!
echo "  → PID: $BACKEND_PID"

# 等待后端启动
sleep 5

# 检查后端
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "[✓] 后端API已就绪: https://localhost:8443"
    echo "    → API文档: https://localhost:8443/docs"
else
    echo "[✗] 后端启动失败"
    exit 1
fi

echo ""
echo "[2/3] 启动前端开发服务器..."
cd "$SCRIPT_DIR/frontend"
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
echo "  → PID: $FRONTEND_PID"

echo ""
echo "[3/3] 启动HTTP→HTTPS重定向 (端口 8080)..."
python3 -c "
import http.server, socketserver
class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header('Location', 'https://' + self.headers['Host'].split(':')[0] + ':8443' + self.path)
        self.end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(('0.0.0.0', 8080), RedirectHandler)
httpd.serve_forever()
" &
REDIRECT_PID=$!
echo "  → PID: $REDIRECT_PID"

echo ""
echo "================================"
echo "  ✅ 所有服务已启动!"
echo "================================"
echo ""
echo "  HTTPS访问 (推荐): https://服务器IP:8443"
echo "  前端开发:         http://localhost:5173"
echo ""
echo "  测试账号:"
echo "    管理员: admin / admin123"
echo "    学员:   lisi  / 123456"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "echo '正在停止...'; kill $BACKEND_PID $FRONTEND_PID $REDIRECT_PID 2>/dev/null; exit" INT TERM

# 保持运行
wait
