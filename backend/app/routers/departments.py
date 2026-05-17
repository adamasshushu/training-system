"""部门管理路由"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.department import Department
from app.models.user import User
from app.utils.auth import get_current_user
from app.schemas.user import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


def _build_tree(depts: list, parent_id: Optional[int] = None) -> list:
    """递归构建部门树"""
    tree = []
    for d in depts:
        if d.get("上级部门ID") == parent_id:
            children = _build_tree(depts, d.get("ID"))
            d["子部门"] = children
            tree.append(d)
    return tree


@router.get("")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取部门树形列表"""
    result = await db.execute(
        select(Department).where(Department.is_active == True).order_by(Department.sort)
    )
    departments = result.scalars().all()

    dept_list = []
    for d in departments:
        # 统计每个部门的员工数
        user_count_result = await db.execute(
            select(User).where(
                User.department_id == d.id,
                User.is_active == True
            )
        )
        user_count = len(user_count_result.scalars().all())
        dept_list.append({
            "ID": d.id,
            "名称": d.name,
            "上级部门ID": d.parent_id,
            "排序": d.sort,
            "是否激活": d.is_active,
            "员工数量": user_count,
        })

    tree = _build_tree(dept_list)
    return {
        "数据": tree,
        "共计": len(departments),
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("")
async def create_department(
    req: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建部门"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可创建部门")
    dept = Department(
        name=req.名称,
        parent_id=req.上级部门ID,
        sort=req.排序,
    )
    db.add(dept)
    await db.flush()
    return {
        "ID": dept.id,
        "名称": dept.name,
        "message": "部门创建成功",
        "labels": {"ID": "id", "名称": "name", "message": "消息"}
    }


@router.put("/{dept_id}")
async def update_department(
    dept_id: int,
    req: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新部门"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可更新部门")
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    if req.名称 is not None:
        dept.name = req.名称
    if req.上级部门ID is not None:
        dept.parent_id = req.上级部门ID
    if req.排序 is not None:
        dept.sort = req.排序
    if req.是否激活 is not None:
        dept.is_active = req.是否激活
    await db.flush()
    return {
        "ID": dept.id,
        "名称": dept.name,
        "message": "部门更新成功",
        "labels": {"ID": "id", "名称": "name", "message": "消息"}
    }


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除部门"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除部门")
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    # 检查是否有子部门
    children_result = await db.execute(
        select(Department).where(Department.parent_id == dept_id)
    )
    if children_result.scalars().first():
        raise HTTPException(status_code=400, detail="请先删除子部门")
    # 检查是否有用户
    user_result = await db.execute(
        select(User).where(User.department_id == dept_id)
    )
    if user_result.scalars().first():
        raise HTTPException(status_code=400, detail="该部门下还有用户，无法删除")
    dept.is_active = False
    await db.flush()
    return {"message": "部门已停用", "labels": {"message": "消息"}}
