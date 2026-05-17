"""课程反馈评分模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CourseReview(Base):
    """课程评价"""
    __tablename__ = "course_reviews"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False, comment="评分 1-5")
    content = Column(Text, nullable=True, comment="评价内容")
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", backref="reviews", lazy="selectin")
    user = relationship("User", lazy="selectin")


class TrainerFeedback(Base):
    """培训系统反馈（非课程评价，针对系统本身）"""
    __tablename__ = "trainer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("training_tasks.id"), nullable=True, comment="关联任务")
    content_rating = Column(Integer, default=3, comment="培训内容评分 1-5")
    system_rating = Column(Integer, default=3, comment="系统体验评分 1-5")
    suggestion = Column(Text, nullable=True, comment="建议")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
