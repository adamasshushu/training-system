"""用户相关Pydantic模型"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ========== 登录 ==========

class LoginRequest(BaseModel):
    """登录请求"""
    用户名: str = Field(..., alias="username")
    密码: str = Field(..., alias="password")

    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., alias="access_token")
    token_type: str = Field("bearer", alias="token_type")
    用户信息: Any = None
    labels: dict = {
        "access_token": "访问令牌",
        "token_type": "令牌类型",
        "用户信息": "user_info"
    }

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    用户信息: Optional[Any] = None


# ========== 用户 ==========

class UserCreate(BaseModel):
    """创建用户"""
    用户名: str = Field(..., alias="username", min_length=2, max_length=50)
    真实姓名: str = Field(..., alias="real_name")
    密码: str = Field(..., alias="password", min_length=6)
    邮箱: Optional[str] = Field(None, alias="email")
    手机号: Optional[str] = Field(None, alias="phone")
    角色: str = Field("student", alias="role", pattern="^(admin|teacher|student)$")
    部门ID: Optional[int] = Field(None, alias="department_id")

    class Config:
        populate_by_name = True


class UserUpdate(BaseModel):
    """更新用户"""
    真实姓名: Optional[str] = Field(None, alias="real_name")
    邮箱: Optional[str] = Field(None, alias="email")
    手机号: Optional[str] = Field(None, alias="phone")
    角色: Optional[str] = Field(None, alias="role", pattern="^(admin|teacher|student)$")
    部门ID: Optional[int] = Field(None, alias="department_id")
    是否激活: Optional[bool] = Field(None, alias="is_active")

    class Config:
        populate_by_name = True


class UserPasswordReset(BaseModel):
    """管理员重置用户密码"""
    新密码: str = Field(..., alias="new_password", min_length=6)

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """用户响应"""
    ID: int = Field(..., alias="id")
    用户名: str = Field(..., alias="username")
    真实姓名: str = Field(..., alias="real_name")
    邮箱: Optional[str] = Field(None, alias="email")
    手机号: Optional[str] = Field(None, alias="phone")
    角色: str = Field(..., alias="role")
    部门ID: Optional[int] = Field(None, alias="department_id")
    部门名称: Optional[str] = None
    是否激活: bool = Field(True, alias="is_active")
    创建时间: Optional[str] = Field(None, alias="created_at")
    labels: dict = {
        "ID": "id",
        "用户名": "username",
        "真实姓名": "real_name",
        "邮箱": "email",
        "手机号": "phone",
        "角色": "role",
        "部门ID": "department_id",
        "部门名称": "department_name",
        "是否激活": "is_active",
        "创建时间": "created_at"
    }

    class Config:
        populate_by_name = True


class UserDetailResponse(BaseModel):
    """用户详情（含部门信息）"""
    ID: int
    用户名: str
    真实姓名: str
    邮箱: Optional[str] = None
    手机号: Optional[str] = None
    角色: str
    部门ID: Optional[int] = None
    部门名称: Optional[str] = None
    是否激活: bool = True
    创建时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "用户名": "username",
        "真实姓名": "real_name",
        "邮箱": "email",
        "手机号": "phone",
        "角色": "role",
        "部门ID": "department_id",
        "部门名称": "department_name",
        "是否激活": "is_active",
        "创建时间": "created_at"
    }


# ========== 部门 ==========

class DepartmentCreate(BaseModel):
    """创建部门"""
    名称: str = Field(..., alias="name", min_length=1, max_length=100)
    上级部门ID: Optional[int] = Field(None, alias="parent_id")
    排序: int = Field(0, alias="sort")

    class Config:
        populate_by_name = True


class DepartmentUpdate(BaseModel):
    """更新部门"""
    名称: Optional[str] = Field(None, alias="name")
    上级部门ID: Optional[int] = Field(None, alias="parent_id")
    排序: Optional[int] = Field(None, alias="sort")
    是否激活: Optional[bool] = Field(None, alias="is_active")

    class Config:
        populate_by_name = True


class DepartmentResponse(BaseModel):
    """部门响应"""
    ID: int = Field(..., alias="id")
    名称: str = Field(..., alias="name")
    上级部门ID: Optional[int] = Field(None, alias="parent_id")
    排序: int = Field(0, alias="sort")
    是否激活: bool = Field(True, alias="is_active")
    子部门: Optional[List[Any]] = []
    员工数量: int = 0
    labels: dict = {
        "ID": "id",
        "名称": "name",
        "上级部门ID": "parent_id",
        "排序": "sort",
        "是否激活": "is_active",
        "子部门": "children",
        "员工数量": "user_count"
    }

    class Config:
        populate_by_name = True


class DepartmentListResponse(BaseModel):
    """部门列表响应"""
    数据: List[DepartmentResponse]
    共计: int
    labels: dict = {
        "数据": "data",
        "共计": "total"
    }
