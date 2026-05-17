"""证书相关Pydantic模型"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CertificateTemplateCreate(BaseModel):
    """创建证书模板"""
    名称: str = Field(..., alias="name", min_length=1, max_length=100)
    背景图: Optional[str] = Field(None, alias="background")
    样式配置: Optional[str] = Field(None, alias="style_config")

    class Config:
        populate_by_name = True


class CertificateTemplateResponse(BaseModel):
    """证书模板响应"""
    ID: int = Field(..., alias="id")
    名称: str = Field(..., alias="name")
    背景图: Optional[str] = Field(None, alias="background")
    样式配置: Optional[str] = Field(None, alias="style_config")
    是否激活: bool = Field(True, alias="is_active")
    创建时间: Optional[str] = Field(None, alias="created_at")
    labels: dict = {
        "ID": "id",
        "名称": "name",
        "背景图": "background",
        "样式配置": "style_config",
        "是否激活": "is_active",
        "创建时间": "created_at"
    }

    class Config:
        populate_by_name = True


class CertificateIssueRequest(BaseModel):
    """发放证书"""
    用户ID: int = Field(..., alias="user_id")
    模板ID: Optional[int] = Field(None, alias="template_id")
    任务ID: Optional[int] = Field(None, alias="task_id")
    证书编号: Optional[str] = Field(None, alias="cert_number")
    持证人姓名: Optional[str] = Field(None, alias="user_name")

    class Config:
        populate_by_name = True


class CertificateResponse(BaseModel):
    """证书响应"""
    ID: int = Field(..., alias="id")
    用户ID: int = Field(..., alias="user_id")
    用户姓名: Optional[str] = None
    模板ID: Optional[int] = Field(None, alias="template_id")
    模板名称: Optional[str] = None
    任务ID: Optional[int] = Field(None, alias="task_id")
    证书编号: Optional[str] = Field(None, alias="cert_number")
    持证人姓名: Optional[str] = Field(None, alias="user_name")
    发放时间: Optional[str] = Field(None, alias="issued_at")
    labels: dict = {
        "ID": "id",
        "用户ID": "user_id",
        "用户姓名": "user_real_name",
        "模板ID": "template_id",
        "模板名称": "template_name",
        "任务ID": "task_id",
        "证书编号": "cert_number",
        "持证人姓名": "user_name",
        "发放时间": "issued_at"
    }

    class Config:
        populate_by_name = True
