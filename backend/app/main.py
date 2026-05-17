"""培训管理系统 - FastAPI 应用入口"""
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import init_db, async_session_factory
from app.models.user import User
from app.models.department import Department
from app.utils.auth import get_password_hash


# ========== 中间件：去除末尾斜杠 ==========

class StripTrailingSlashMiddleware(BaseHTTPMiddleware):
    """将所有以斜杠结尾的URL重定向到无斜杠版本（根路径除外）"""
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # 保留根路径，去掉其他路径的末尾斜杠
        if path != "/" and path.endswith("/"):
            new_path = path.rstrip("/")
            from starlette.responses import RedirectResponse
            return RedirectResponse(url=new_path, status_code=307)
        response = await call_next(request)
        return response


# ========== 种子数据初始化 ==========

async def seed_data():
    """初始化种子数据：管理员账号、部门、示例员工"""
    async with async_session_factory() as db:
        try:
            # 1. 创建管理员账号
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            admin = result.scalar_one_or_none()
            if not admin:
                admin = User(
                    username="admin",
                    real_name="系统管理员",
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    email="admin@company.com",
                    is_active=True,
                )
                db.add(admin)
                await db.flush()
                print("[种子数据] 管理员账号已创建: admin / admin123")
            else:
                print("[种子数据] 管理员账号已存在，跳过")

            # 2. 创建默认部门
            departments_data = [
                {"name": "技术部", "sort": 1, "parent_id": None},
                {"name": "产品部", "sort": 2, "parent_id": None},
                {"name": "人事部", "sort": 3, "parent_id": None},
            ]
            dept_map = {}
            for dept_info in departments_data:
                result = await db.execute(
                    select(Department).where(Department.name == dept_info["name"])
                )
                existing = result.scalar_one_or_none()
                if not existing:
                    dept = Department(
                        name=dept_info["name"],
                        sort=dept_info["sort"],
                        parent_id=dept_info["parent_id"],
                        is_active=True,
                    )
                    db.add(dept)
                    await db.flush()
                    dept_map[dept_info["name"]] = dept.id
                    print(f"[种子数据] 部门已创建: {dept_info['name']}")
                else:
                    dept_map[dept_info["name"]] = existing.id
                    print(f"[种子数据] 部门已存在: {dept_info['name']}")

            # 3. 在每个部门下创建示例员工
            employee_data = [
                # 技术部员工
                {"username": "zhangsan", "real_name": "张三", "password": "123456", "role": "teacher", "dept": "技术部"},
                {"username": "lisi", "real_name": "李四", "password": "123456", "role": "student", "dept": "技术部"},
                {"username": "wangwu", "real_name": "王五", "password": "123456", "role": "student", "dept": "技术部"},
                # 产品部员工
                {"username": "zhaoliu", "real_name": "赵六", "password": "123456", "role": "teacher", "dept": "产品部"},
                {"username": "sunqi", "real_name": "孙七", "password": "123456", "role": "student", "dept": "产品部"},
                {"username": "zhouba", "real_name": "周八", "password": "123456", "role": "student", "dept": "产品部"},
                # 人事部员工
                {"username": "wujiu", "real_name": "吴九", "password": "123456", "role": "teacher", "dept": "人事部"},
                {"username": "zhengshi", "real_name": "郑十", "password": "123456", "role": "student", "dept": "人事部"},
            ]

            emp_count = 0
            for emp in employee_data:
                result = await db.execute(
                    select(User).where(User.username == emp["username"])
                )
                existing = result.scalar_one_or_none()
                if not existing:
                    user = User(
                        username=emp["username"],
                        real_name=emp["real_name"],
                        password_hash=get_password_hash(emp["password"]),
                        role=emp["role"],
                        department_id=dept_map.get(emp["dept"]),
                        is_active=True,
                    )
                    db.add(user)
                    emp_count += 1

            if emp_count > 0:
                await db.flush()
                print(f"[种子数据] 已创建 {emp_count} 名示例员工")

            await db.commit()
            print("[种子数据] 初始化完成")

        except Exception as e:
            await db.rollback()
            print(f"[种子数据] 初始化失败: {e}")
            raise


# ========== 应用生命周期 ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭生命周期"""
    # 启动：初始化数据库 + 种子数据
    print(f"[启动] {settings.APP_NAME} v{settings.APP_VERSION}")
    print("[启动] 初始化数据库表...")
    await init_db()
    print("[启动] 数据库表初始化完成")
    print("[启动] 初始化种子数据...")
    await seed_data()
    print("[启动] 所有初始化完成，服务已就绪")
    yield
    # 关闭
    print("[关闭] 应用已停止")


# ========== 创建FastAPI应用 ==========

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业内部培训管理系统 API",
    lifespan=lifespan,
)

# CORS - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 去除末尾斜杠中间件
app.add_middleware(StripTrailingSlashMiddleware)


# ========== 注册路由 ==========

from app.routers import auth, departments, users, courses, exams, tasks, certificates

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(exams.router)
app.include_router(tasks.router)
app.include_router(certificates.router)


# ========== 根路径 ==========

@app.get("/")
async def root():
    return {
        "应用名称": settings.APP_NAME,
        "版本": settings.APP_VERSION,
        "接口文档": "/docs",
        "labels": {
            "应用名称": "app_name",
            "版本": "version",
            "接口文档": "docs_url"
        }
    }


# ========== 健康检查 ==========

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "服务运行正常"}
