# AGENTS.md — 培训管理系统项目规范

## 启动命令
```bash
# 后端
cd /home/cyborg/training-system/backend && source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd /home/cyborg/training-system/frontend && npm run dev -- --host 0.0.0.0
```

## 测试账号
- 管理员: admin / admin123
- 学员: lisi / 123456

## 关键约定
- **中文字段名**: 所有API用中文键(标题/角色/数据/共计)，带labels映射
- **Token**: 登录返回 `access_token` 不是 `token`
- **角色**: admin/teacher/student，路由守卫按角色拦截
- **SQLAlchemy**: 全部 `relationship()` 必须 `lazy="selectin"`
- **前端axios**: 自动unwrap response.data，自动挂Bearer token
- **StripTrailingSlashMiddleware**: 已安装，URL末尾斜杠自动去掉

## 项目结构
- 后端: FastAPI on :8000, 51端点, 7路由模块, 14张表
- 前端: Vue3+Vite on :5173, 20页面, 5API模块
- DB: SQLite at backend/training.db
- 种子数据: main.py 启动时自动创建

## 若失忆：读 README.md 和本文件即可恢复
