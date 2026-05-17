"""课程模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CourseCategory(Base):
    __tablename__ = "course_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, ForeignKey("course_categories.id"), nullable=True)
    sort = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    children = relationship("CourseCategory", backref="parent", remote_side=[id], lazy="selectin")
    courses = relationship("Course", back_populates="category", lazy="selectin")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="课程标题")
    cover = Column(String(255), nullable=True, comment="封面图")
    description = Column(Text, nullable=True, comment="课程简介")
    category_id = Column(Integer, ForeignKey("course_categories.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="讲师")
    is_published = Column(Boolean, default=False, comment="是否发布")
    sort = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("CourseCategory", back_populates="courses", lazy="selectin")
    teacher = relationship("User", lazy="selectin")
    chapters = relationship("Chapter", back_populates="course", order_by="Chapter.sort", lazy="selectin")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    sort = Column(Integer, default=0)

    course = relationship("Course", back_populates="chapters", lazy="selectin")
    lessons = relationship("Lesson", back_populates="chapter", order_by="Lesson.sort", lazy="selectin")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(200), nullable=False)
    lesson_type = Column(String(20), nullable=False, comment="课时类型: video/document/text")
    content_text = Column(Text, nullable=True, comment="图文内容")
    file_url = Column(String(255), nullable=True, comment="视频/文档地址")
    duration = Column(Integer, default=0, comment="时长(秒)")
    sort = Column(Integer, default=0)
    is_free = Column(Boolean, default=False, comment="是否免费试看")

    chapter = relationship("Chapter", back_populates="lessons", lazy="selectin")


class CourseProgress(Base):
    """学员学习进度"""
    __tablename__ = "course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress = Column(Float, default=0, comment="进度 0-100")
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
