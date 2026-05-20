# AGENTS.md — 培训管理系统项目规范

## 启动命令
```bash
# 后端
cd /home/cyborg/training-system/backend && source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8004

# 前端
cd /home/cyborg/training-system/frontend && npm run dev -- --host 0.0.0.0
```

## 测试账号
- 管理员: admin / admin123
- 学员: lisi / 123456

## 启动方式

### 开发模式（前端+Vite热更新）
### 开发模式（前端+Vite热更新）
```bash
# 后端（HTTPS）
cd /home/cyborg/training-system/backend && source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-certfile=cert.pem --ssl-keyfile=key.pem

# 前端热更新（HTTPS）
cd /home/cyborg/training-system/frontend && npm run dev -- --host 0.0.0.0

# 访问: https://localhost:5173 (前端 HTTPS) 或 https://服务器IP:8443 (统一HTTPS)
```

### 生产模式（一键HTTPS启动）
```bash
cd /home/cyborg/training-system && ./start-https.sh
# 访问: https://服务器IP:8443
# HTTP自动重定向: http://服务器IP:8080 → https://服务器IP:8443
```

### 局域网HTTPS访问
- 使用内置自签名证书（cert.pem / key.pem）
- 浏览器首次访问会提示"不安全"，点击"高级"→"继续访问"即可
- 适用于内网/局域网环境，无需公网证书

## 关键约定
- **中文字段名**: 所有API用中文键(标题/角色/数据/共计)，带labels映射
- **Token**: 登录返回 `access_token` 不是 `token`
- **角色**: admin/teacher/student，路由守卫按角色拦截
- **SQLAlchemy**: 全部 `relationship()` 必须 `lazy="selectin"`
- **前端axios**: 自动unwrap response.data，自动挂Bearer token
- **StripTrailingSlashMiddleware**: 已安装，URL末尾斜杠自动去掉

## 项目结构
- 后端: FastAPI on :8000, 80+端点, 19路由模块, 21张表
  - 路由: auth, departments, users, courses, exams, tasks, certificates, uploads, system, fetch_url, learning_paths, progress, dashboard, enterprise, reviews, notifications, bookmarks, knowledge_graph, reports
  - 模型: file_records, system_settings, learning_paths, learning_path_courses, user_learning_paths, enterprise_configs, course_reviews, trainer_feedback, notifications, course_bookmarks, lesson_notes
- 前端: Vue3+Vite on :5173, 32页面, 5API模块
  - Admin: Dashboard, Departments, Users, Courses, CourseCategories, Exams, Questions, Tasks, Certificates, CertificateTemplates,
           LearningPaths, ProgressDashboard, FileManager, OnlineEditor, FetchUrl, SystemSettings, EnterpriseSettings, FeedbackManage,
           ReportExport, KnowledgeGraph
  - Student: Dashboard(Gantt+Paths), Courses, CourseDetail, LessonPlayer, Exams, ExamTaking, Tasks, Certificates,
             Notifications, Feedback, Bookmarks, KnowledgeGraph

## 若失忆：读 README.md 和本文件即可恢复
