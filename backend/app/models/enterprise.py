"""企业平台模型：存储各平台配置"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class EnterpriseConfig(Base):
    """企业平台配置（钉钉/飞书/企微）"""
    __tablename__ = "enterprise_configs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False, comment="平台: dingtalk/feishu/wecom")
    is_enabled = Column(Boolean, default=False, comment="是否启用")
    config_json = Column(Text, nullable=True, comment="配置JSON(AppKey/Secret/AgentId等)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
