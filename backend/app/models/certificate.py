"""证书模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CertificateTemplate(Base):
    """证书模板"""
    __tablename__ = "certificate_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    background = Column(String(255), nullable=True, comment="背景图")
    style_config = Column(Text, nullable=True, comment="样式配置(JSON)")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Certificate(Base):
    """已发放证书"""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("certificate_templates.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("training_tasks.id"), nullable=True)
    cert_number = Column(String(50), unique=True, comment="证书编号")
    user_name = Column(String(50), comment="持证人姓名")
    issued_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", lazy="selectin")
