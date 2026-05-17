# 🎓 培训管理系统 (Training System)

企业内部培训管理平台，覆盖课程学习、在线考试、培训任务、证书发放完整业务闭环。

**技术栈**：FastAPI + Vue3/Element Plus + SQLite | 51 API 端点 + 20 前端页面

---

## 🚀 快速启动

```bash
# 1. 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 前端 (新终端)
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

访问 `http://localhost:5173`

### 测试账号

| 角色 | 用户名 | 密码 | 入口 |
|------|--------|------|------|
| 管理员 | admin | admin123 | `/admin` |
| 学员 | lisi | 123456 | `/student` |
| 讲师 | zhangsan | 123456 | `/admin` |

其他学员账号：wangwu / sunqi / zhouba / zhengshi（密码均为 123456）

---

## 📐 系统架构

```
training-system/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 应用入口 + 种子数据 + 中间件
│   │   ├── config.py          # JWT密钥、数据库URL等配置
│   │   ├── database.py        # 异步 SQLAlchemy 引擎
│   │   ├── models/            # 14 张数据库表
│   │   │   ├── department.py  # 部门（树形结构）
│   │   │   ├── user.py        # 用户（admin/teacher/student）
│   │   │   ├── course.py      # 课程/分类/章节/课时/学习进度
│   │   │   ├── exam.py        # 题库/试卷/试卷题目/考试结果
│   │   │   ├── task.py        # 培训任务/关联课程/关联考试/指派
│   │   │   └── certificate.py # 证书模板/已发放证书
│   │   ├── routers/           # 7 个路由模块
│   │   │   ├── auth.py        # 登录/注册/个人信息
│   │   │   ├── departments.py # 部门 CRUD + 树形列表
│   │   │   ├── users.py       # 用户 CRUD + 筛选搜索
│   │   │   ├── courses.py     # 课程/分类/章节/课时/进度
│   │   │   ├── exams.py       # 题库/试卷/作答/判分
│   │   │   ├── tasks.py       # 任务/指派/进度追踪
│   │   │   └── certificates.py# 模板/发证/学员证书/看板
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   └── utils/auth.py      # JWT 生成/验证 + 密码哈希
│   ├── training.db            # SQLite 数据库（启动自动创建）
│   └── requirements.txt
├── frontend/                   # Vue3 + Element Plus 前端
│   └── src/
│       ├── api/               # axios API 封装
│       │   ├── auth.js        # 登录/退出/用户信息
│       │   ├── courses.js     # 课程/分类/章节/课时/进度
│       │   ├── exams.js       # 题库/试卷/作答/成绩
│       │   ├── tasks.js       # 任务/指派/进度
│       │   └── certificates.js# 模板/证书/看板
│       ├── views/
│       │   ├── admin/         # 10 个管理后台页面
│       │   │   ├── Dashboard.vue        # 数据看板
│       │   │   ├── Departments.vue      # 部门管理
│       │   │   ├── Users.vue            # 员工管理
│       │   │   ├── Courses.vue          # 课程管理
│       │   │   ├── CourseCategories.vue # 课程分类
│       │   │   ├── Questions.vue        # 题库管理
│       │   │   ├── Exams.vue            # 考试管理
│       │   │   ├── Tasks.vue            # 培训任务
│       │   │   ├── Certificates.vue     # 证书管理
│       │   │   └── CertificateTemplates.vue # 证书模板
│       │   ├── student/       # 8 个学员前台页面
│       │   │   ├── Dashboard.vue    # 学习首页
│       │   │   ├── Courses.vue      # 课程中心
│       │   │   ├── CourseDetail.vue # 课程详情
│       │   │   ├── LessonPlayer.vue # 课时学习
│       │   │   ├── Exams.vue        # 我的考试
│       │   │   ├── ExamTaking.vue   # 考试作答
│       │   │   ├── Tasks.vue        # 我的任务
│       │   │   └── Certificates.vue # 我的证书
│       │   └── Login.vue            # 登录页
│       ├── router/index.js   # Vue Router + 角色守卫
│       └── utils/auth.js     # Token / 用户信息存取
└── README.md
```

---

## 📋 功能模块

### 🏗️ 阶段一：基础框架
- JWT 登录/认证
- 角色权限控制（admin / teacher / student）
- 数据库 14 张表自动建表
- 种子数据：3 部门 + 9 员工

### 📚 阶段二：课程管理
- 课程分类（树形结构）
- 课程 CRUD + 发布/下架
- 章节排序管理
- 课时：视频 / 文档 / 图文三种类型
- 学员学习进度追踪

### 📝 阶段三：考试系统
- 题库：单选 / 多选 / 判断 / 填空 / 简答 5 种题型
- 题型筛选 + 关键词搜索 + 分页
- 试卷组卷（从题库选题，设置分值）
- 学员在线作答：倒计时 + 答题卡 + 自动提交
- 自动判分（客观题精确匹配，多选用逗号分隔集合匹配）
- 成绩查询

### 🎯 阶段四：培训任务
- 任务 CRUD
- 自由模式 / 闯关模式
- 关联多门课程 + 多场考试
- 指派到部门或指定学员
- 学员进度追踪（课程完成百分比 + 考试通过状态）

### 🏆 阶段五：证书系统
- 证书模板管理
- 手动发放证书
- 学员查看自己的证书
- 系统数据看板（部门/员工/课程/考试/任务/证书统计）

---

## 🔌 API 端点速查 (51个)

### 认证 (3)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录，返回 `access_token` |
| GET | `/api/auth/me` | 当前用户信息 |
| POST | `/api/auth/register` | 注册（管理员专用） |

### 部门 (4)
| GET | `/api/departments` | 部门树形列表 |
| POST | `/api/departments` | 创建部门 |
| PUT | `/api/departments/{id}` | 更新部门 |
| DELETE | `/api/departments/{id}` | 停用部门 |

### 用户 (4)
| GET | `/api/users` | 用户列表（支持部门/角色/关键词筛选） |
| POST | `/api/users` | 创建用户 |
| PUT | `/api/users/{id}` | 更新用户 |
| DELETE | `/api/users/{id}` | 停用用户 |

### 课程 (12)
| GET | `/api/categories` | 课程分类树 |
| POST | `/api/categories` | 创建分类 |
| GET | `/api/courses` | 课程列表 |
| GET | `/api/courses/student` | 学员端课程（仅已发布） |
| GET | `/api/courses/{id}` | 课程详情（含章节课时） |
| POST | `/api/courses` | 创建课程 |
| PUT | `/api/courses/{id}` | 更新课程 |
| DELETE | `/api/courses/{id}` | 删除课程 |
| POST | `/api/courses/{id}/chapters` | 创建章节 |
| POST | `/api/courses/{id}/lessons` | 创建课时 |
| POST | `/api/courses/{id}/progress` | 更新学习进度 |

### 考试 (11)
| GET | `/api/questions` | 题库列表（题型/关键词筛选） |
| POST | `/api/questions` | 创建题目 |
| PUT | `/api/questions/{id}` | 更新题目 |
| DELETE | `/api/questions/{id}` | 删除题目 |
| GET | `/api/exams` | 试卷列表 |
| POST | `/api/exams` | 创建试卷（含选题） |
| GET | `/api/exams/{id}` | 试卷详情（含题目） |
| PUT | `/api/exams/{id}` | 更新试卷 |
| DELETE | `/api/exams/{id}` | 删除试卷 |
| POST | `/api/exams/{id}/submit` | 提交作答并自动判分 |
| GET | `/api/exams/{id}/results` | 考试成绩 |

### 任务 (9)
| GET | `/api/tasks` | 任务列表 |
| GET | `/api/tasks/my` | 我的任务（学员端） |
| POST | `/api/tasks` | 创建任务（含关联课程/考试） |
| GET | `/api/tasks/{id}` | 任务详情 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| POST | `/api/tasks/{id}/assign` | 指派到部门/用户 |
| DELETE | `/api/tasks/{id}/assign/{aid}` | 取消指派 |
| GET | `/api/tasks/{id}/progress` | 学员进度 |

### 证书 (8)
| GET | `/api/certificates/templates` | 模板列表 |
| POST | `/api/certificates/templates` | 创建模板 |
| PUT | `/api/certificates/templates/{id}` | 更新模板 |
| DELETE | `/api/certificates/templates/{id}` | 停用模板 |
| GET | `/api/certificates` | 证书列表 |
| POST | `/api/certificates/issue` | 发放证书 |
| GET | `/api/certificates/my` | 我的证书（学员端） |
| GET | `/api/certificates/stats` | 系统看板数据 |

---

## 🎨 前端页面 (20个)

### 管理后台 (10)
| 页面 | 路由 | 功能 |
|------|------|------|
| 数据看板 | `/admin/dashboard` | 7 项核心指标统计 |
| 部门管理 | `/admin/departments` | 树形 CRUD + 员工数 |
| 员工管理 | `/admin/users` | 角色/部门筛选 CRUD |
| 课程管理 | `/admin/courses` | 课程 + 章节 + 课时 CRUD |
| 课程分类 | `/admin/course-categories` | 分类树形 CRUD |
| 题库管理 | `/admin/questions` | 5 种题型 + 搜索分页 |
| 考试管理 | `/admin/exams` | 试卷 + 选题组卷 |
| 培训任务 | `/admin/tasks` | 选课/选考 + 指派 |
| 证书管理 | `/admin/certificates` | 发证 + 列表 |
| 证书模板 | `/admin/certificate-templates` | 模板 CRUD |

### 学员前台 (8)
| 页面 | 路由 | 功能 |
|------|------|------|
| 学习首页 | `/student/dashboard` | 课程/考试/任务概览 |
| 课程中心 | `/student/courses` | 浏览已发布课程 |
| 课程详情 | `/student/courses/:id` | 章节 + 课时列表 |
| 课时学习 | `/student/courses/:cid/lessons/:lid` | 视频/图文学习 |
| 我的考试 | `/student/exams` | 待完成 + 已完成 |
| 考试作答 | `/student/exams/:id` | 答题卡 + 倒计时 + 提交 |
| 我的任务 | `/student/tasks` | 任务进度追踪 |
| 我的证书 | `/student/certificates` | 已获证书列表 |

### 公共 (2)
| 登录页 | `/login` | 统一登录入口 |

---

## 🔑 关键约定

### API 设计
- **中文字段名**：所有请求/响应使用中文键名（`标题`/`角色`/`数据`/`共计`）
- **响应结构**：列表统一返回 `{"数据": [...], "共计": N, "labels": {...}}`
- **Token**：登录返回字段为 `access_token`（非 `token`）
- **角色**：`admin`/`teacher`/`student`，路由守卫按角色拦截

### 数据库
- **SQLite** 单文件存储，首次启动自动建表
- **种子数据**：`main.py` 启动时自动创建部门、管理员、讲师、学员
- **所有 `relationship()` 必须 `lazy="selectin"`**（异步 SQLAlchemy 防 MissingGreenlet）

### 前端
- **axios 拦截器**自动 unwrap `response.data`，自动挂 Bearer token
- **Vite 代理** `/api` → `http://localhost:8000`
- **手机端响应式**：Element Plus 栅格适配

---

## 🛠️ 常见问题

| 问题 | 解决方案 |
|------|----------|
| 登录闪退 | Token字段应为 `res.access_token`，检查 `Login.vue` |
| 后台 500 MissingGreenlet | 所有 `relationship()` 需加 `lazy="selectin"` |
| 401 未授权 | 确认密码：管理员 `admin123`，其他用户 `123456` |
| 数据库只读 | `chmod 644 backend/training.db` |
| 端口冲突 | `pkill -f "uvicorn\|vite"` 后重启 |

---

## 📄 License

MIT

---

**Made with ❤️ by Adamas | Powered by FastAPI + Vue3**
