#!/bin/bash
# 培训管理系统 — PostgreSQL 生产环境一键部署
# 请手动运行: bash /home/cyborg/training-system/backend/setup-postgres.sh

set -e

echo "========================================"
echo "  培训管理系统 PostgreSQL 部署"
echo "========================================"
echo ""

# 1. 安装 PostgreSQL
echo "[1/5] 安装 PostgreSQL..."
sudo apt-get update -qq
sudo apt-get install -y postgresql postgresql-client > /dev/null 2>&1
echo "  ✅ PostgreSQL 已安装"

# 2. 启动服务
echo "[2/5] 启动 PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo "  ✅ 服务已启动"

# 3. 创建数据库和用户
echo "[3/5] 创建数据库 training_db..."
sudo -u postgres psql -c "CREATE USER training_user WITH PASSWORD 'Tr4in1ng_DB_P@ss_2025';" 2>/dev/null || echo "  用户已存在，跳过"
sudo -u postgres psql -c "CREATE DATABASE training_db OWNER training_user;" 2>/dev/null || echo "  数据库已存在，跳过"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE training_db TO training_user;"
echo "  ✅ 数据库已创建"

# 4. 更新 .env 配置
echo "[4/5] 更新配置文件..."
cat > /home/cyborg/training-system/backend/.env << 'ENVEOF'
# 培训管理系统 — PostgreSQL 生产环境
SECRET_KEY=Tr4in1ng-Syst3m-Pr0d-K3y-2025!@#SECURE
DATABASE_URL=postgresql+asyncpg://training_user:Tr4in1ng_DB_P%40ss_2025@localhost:5432/training_db
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
STORAGE_MODE=local
ENVEOF
echo "  ✅ .env 已更新"

# 5. 安装 asyncpg
echo "[5/5] 安装 asyncpg..."
source ../venv/bin/activate
pip install asyncpg -q
echo "  ✅ asyncpg 已安装"

echo ""
echo "========================================"
echo "  ✅ 部署完成！"
echo "========================================"
echo ""
echo "接下来手动执行："
echo "  1. 启动服务: cd /home/cyborg/training-system/backend && bash start-prod.sh"
echo "  2. 测试连接: curl http://localhost:8004/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
echo ""
echo "数据库信息："
echo "  地址: localhost:5432"
echo "  库名: training_db"
echo "  用户: training_user"
echo "  密码: Tr4in1ng_DB_P@ss_2025"
