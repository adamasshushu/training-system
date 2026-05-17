"""认证路由：登录、注册、获取当前用户"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.utils.auth import (
    create_access_token, get_password_hash, verify_password, get_current_user
)
from app.schemas.user import LoginRequest, UserCreate, UserResponse, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录，返回JWT令牌"""
    result = await db.execute(
        select(User).where(User.username == req.用户名)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.密码, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )
    token = create_access_token({
        "sub": user.username,
        "id": user.id,
        "role": user.role,
    })
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        用户信息={
            "ID": user.id,
            "用户名": user.username,
            "真实姓名": user.real_name,
            "角色": user.role,
        }
    )


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户信息"""
    result = await db.execute(
        select(User).where(User.id == current_user["id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "ID": user.id,
        "用户名": user.username,
        "真实姓名": user.real_name,
        "邮箱": user.email,
        "手机号": user.phone,
        "角色": user.role,
        "部门ID": user.department_id,
        "是否激活": user.is_active,
        "创建时间": str(user.created_at) if user.created_at else None,
        "labels": {
            "ID": "id",
            "用户名": "username",
            "真实姓名": "real_name",
            "邮箱": "email",
            "手机号": "phone",
            "角色": "role",
            "部门ID": "department_id",
            "是否激活": "is_active",
            "创建时间": "created_at"
        }
    }


@router.post("/register")
async def register(
    req: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """注册新用户（仅管理员）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建用户")
    # 检查用户名唯一性
    result = await db.execute(
        select(User).where(User.username == req.用户名)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.用户名,
        real_name=req.真实姓名,
        email=req.邮箱,
        phone=req.手机号,
        password_hash=get_password_hash(req.密码),
        role=req.角色,
        department_id=req.部门ID,
    )
    db.add(user)
    await db.flush()
    return {
        "message": "用户创建成功",
        "ID": user.id,
        "用户名": user.username,
        "labels": {"message": "消息", "ID": "id", "用户名": "username"}
    }
