"""收藏与笔记模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class CourseBookmark(Base):
    """课程收藏"""
    __tablename__ = "course_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course_bookmark"),)


class LessonNote(Base):
    """课时笔记"""
    __tablename__ = "lesson_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    content = Column(Text, nullable=False, comment="笔记内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
