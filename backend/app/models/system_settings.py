"""系统设置模型"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base


class SystemSetting(Base):
    """系统设置（键值对）"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False, comment="设置键")
    value = Column(Text, nullable=True, comment="设置值")
    description = Column(String(500), nullable=True, comment="说明")
