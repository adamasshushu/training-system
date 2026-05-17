"""用户管理路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.user import User
from app.models.department import Department
from app.utils.auth import get_password_hash, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("")
async def list_users(
    department_id: Optional[int] = Query(None, alias="department_id"),
    role: Optional[str] = Query(None, alias="role"),
    keyword: Optional[str] = Query(None, alias="keyword"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户列表，支持部门筛选、角色筛选、关键词搜索"""
    query = select(User)
    if department_id:
        query = query.where(User.department_id == department_id)
    if role:
        query = query.where(User.role == role)
    if keyword:
        query = query.where(
            or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword),
                User.email.contains(keyword),
            )
        )
    query = query.order_by(User.id)
    result = await db.execute(query)
    users = result.scalars().all()

    # 分页
    total = len(users)
    start = (page - 1) * page_size
    end = start + page_size
    page_users = users[start:end]

    user_list = []
    for u in page_users:
        dept_name = None
        if u.department_id:
            dept_result = await db.execute(
                select(Department).where(Department.id == u.department_id)
            )
            dept = dept_result.scalar_one_or_none()
            if dept:
                dept_name = dept.name
        user_list.append({
            "ID": u.id,
            "用户名": u.username,
            "真实姓名": u.real_name,
            "邮箱": u.email,
            "手机号": u.phone,
            "角色": u.role,
            "部门ID": u.department_id,
            "部门名称": dept_name,
            "是否激活": u.is_active,
            "创建时间": str(u.created_at) if u.created_at else None,
        })

    return {
        "数据": user_list,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {
            "数据": "data",
            "共计": "total",
            "页码": "page",
            "每页数量": "page_size"
        }
    }


@router.post("")
async def create_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建用户（仅管理员）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建用户")
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


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    req: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新用户信息"""
    if current_user.get("角色") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="无权限修改该用户")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if req.真实姓名 is not None:
        user.real_name = req.真实姓名
    if req.邮箱 is not None:
        user.email = req.邮箱
    if req.手机号 is not None:
        user.phone = req.手机号
    if req.角色 is not None and current_user.get("角色") == "admin":
        user.role = req.角色
    if req.部门ID is not None and current_user.get("角色") == "admin":
        user.department_id = req.部门ID
    if req.是否激活 is not None and current_user.get("角色") == "admin":
        user.is_active = req.是否激活
    await db.flush()
    return {
        "message": "用户更新成功",
        "ID": user.id,
        "labels": {"message": "消息", "ID": "id"}
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除（停用）用户"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除用户")
    if current_user.get("id") == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = False
    await db.flush()
    return {"message": "用户已停用", "labels": {"message": "消息"}}
