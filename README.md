# 培训管理系统 v2.2

> 企业员工培训管理平台 — 课程、考试、证书、学习路径一站式管理

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
# 后端 (HTTPS :8443)
cd backend && bash start-prod.sh

# 前端 (HTTPS :5173)
cd frontend && bash start.sh
```

### 方式二：HTTP 模式（仅开发环境）

```bash
# 后端 HTTP
cd backend && PORT=8004 bash start-prod.sh --http

# 前端会自动代理到后端
cd frontend && PORT=5173 npx vite --host 0.0.0.0
```

---

## ⚙️ 配置说明

### 🔢 修改端口

| 组件 | 修改方式 | 默认值 |
|------|---------|--------|
| **后端 HTTPS** | `PORT=9443 bash start-prod.sh` | 8443 |
| **后端 HTTP** | `PORT=9000 bash start-prod.sh --http` | 8004 |
| **前端** | `PORT=3000 bash start.sh` | 5173 |
| **后端代理地址** | 修改 `frontend/vite.config.js` 中 `BACKEND_PORT` | 8443 |

也可以在 `.env` 中永久设置：
```env
# backend/.env
PORT=9443
HOST=0.0.0.0
```

### 🔐 HTTPS 证书

- **自签名证书**: `backend/cert.pem` + `backend/key.pem`（365天有效期）
- 浏览器首次访问会提示"不安全" → 点击"高级" → "继续访问"
- 生产环境请替换为正式 CA 证书（Let's Encrypt / 阿里云 / 腾讯云）
- **重新生成证书**:
  ```bash
  cd backend
  openssl req -x509 -newkey rsa:2048 -nodes \
      -keyout key.pem -out cert.pem -days 365 \
      -subj "/CN=你的域名或IP"
  cp cert.pem key.pem ../frontend/
  ```

---

## 🗄️ 数据库配置

### SQLite（当前使用）

| 项目 | 值 |
|------|-----|
| **文件** | `backend/training_prod.db` |
| **模式** | WAL（高性能读写并发） |
| **位置** | `sqlite+aiosqlite:///./training_prod.db` |
| **用户名/密码** | ❌ 无需认证 |

### PostgreSQL（推荐生产环境）

| 项目 | 值 |
|------|-----|
| **地址** | `localhost:5432` |
| **数据库名** | `training_db` |
| **用户名** | `training_user` |
| **密码** | `Tr4in1ng_DB_P@ss_2025` |
| **连接串** | `postgresql+asyncpg://training_user:Tr4in1ng_DB_P%40ss_2025@localhost:5432/training_db` |

切换到 PostgreSQL：
```bash
# 自动部署
sudo bash backend/setup-postgres.sh

# 或手动修改 backend/.env
DATABASE_URL=postgresql+asyncpg://用户名:密码@主机:5432/库名
```

---

## 🔑 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 学员(示例) | `lisi` | `123456` |

---

## 📂 项目结构

```
training-system/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── routers/          # 22 个路由模块
│   │   ├── models/           # 13 个数据模型
│   │   ├── config.py         # 配置（数据库/JWT/存储）
│   │   ├── database.py       # 数据库连接（WAL 模式）
│   │   └── main.py           # 应用入口
│   ├── cert.pem / key.pem    # SSL 证书
│   ├── .env                  # 环境变量
│   ├── start-prod.sh         # 生产启动脚本
│   ├── setup-postgres.sh     # PostgreSQL 部署脚本
│   └── training_prod.db      # SQLite 生产库
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 可复用组件
│   │   └── styles/           # 设计 Token 系统
│   ├── cert.pem / key.pem    # 前端 SSL 证书
│   ├── vite.config.js        # Vite 配置（HTTPS/代理）
│   └── start.sh              # 前端启动脚本
└── README.md                 # 本文件
```

---

## 🔗 访问地址

| 服务 | 地址 |
|------|------|
| 前端 (HTTPS) | `https://192.168.201.230:5173` |
| 后端 API (HTTPS) | `https://192.168.201.230:8443` |
| API 文档 (后台) | `https://192.168.201.230:8443/docs` |
