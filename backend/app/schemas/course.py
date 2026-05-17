"""课程相关Pydantic模型"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ========== 课程分类 ==========

class CourseCategoryCreate(BaseModel):
    """创建课程分类"""
    名称: str = Field(..., alias="name", min_length=1, max_length=100)
    上级ID: Optional[int] = Field(None, alias="parent_id")
    排序: int = Field(0, alias="sort")

    class Config:
        populate_by_name = True


class CourseCategoryResponse(BaseModel):
    """课程分类响应"""
    ID: int = Field(..., alias="id")
    名称: str = Field(..., alias="name")
    上级ID: Optional[int] = Field(None, alias="parent_id")
    排序: int = Field(0, alias="sort")
    是否激活: bool = Field(True, alias="is_active")
    子分类: Optional[List[Any]] = []
    课程数量: int = 0
    labels: dict = {
        "ID": "id",
        "名称": "name",
        "上级ID": "parent_id",
        "排序": "sort",
        "是否激活": "is_active",
        "子分类": "children",
        "课程数量": "course_count"
    }

    class Config:
        populate_by_name = True


# ========== 课时 ==========

class LessonCreate(BaseModel):
    """创建课时"""
    章节ID: int = Field(..., alias="chapter_id")
    标题: str = Field(..., alias="title", min_length=1, max_length=200)
    课时类型: str = Field("video", alias="lesson_type", pattern="^(video|document|text)$")
    图文内容: Optional[str] = Field(None, alias="content_text")
    文件地址: Optional[str] = Field(None, alias="file_url")
    时长: int = Field(0, alias="duration")
    排序: int = Field(0, alias="sort")
    是否免费: bool = Field(False, alias="is_free")

    class Config:
        populate_by_name = True


class LessonUpdate(BaseModel):
    标题: Optional[str] = Field(None, alias="title")
    课时类型: Optional[str] = Field(None, alias="lesson_type")
    图文内容: Optional[str] = Field(None, alias="content_text")
    文件地址: Optional[str] = Field(None, alias="file_url")
    时长: Optional[int] = Field(None, alias="duration")
    排序: Optional[int] = Field(None, alias="sort")
    是否免费: Optional[bool] = Field(None, alias="is_free")

    class Config:
        populate_by_name = True


class LessonResponse(BaseModel):
    """课时响应"""
    ID: int = Field(..., alias="id")
    章节ID: int = Field(..., alias="chapter_id")
    标题: str = Field(..., alias="title")
    课时类型: str = Field(..., alias="lesson_type")
    图文内容: Optional[str] = Field(None, alias="content_text")
    文件地址: Optional[str] = Field(None, alias="file_url")
    时长: int = Field(0, alias="duration")
    排序: int = Field(0, alias="sort")
    是否免费: bool = Field(False, alias="is_free")
    labels: dict = {
        "ID": "id",
        "章节ID": "chapter_id",
        "标题": "title",
        "课时类型": "lesson_type",
        "图文内容": "content_text",
        "文件地址": "file_url",
        "时长": "duration",
        "排序": "sort",
        "是否免费": "is_free"
    }

    class Config:
        populate_by_name = True


# ========== 章节 ==========

class ChapterCreate(BaseModel):
    """创建章节"""
    标题: str = Field(..., alias="title", min_length=1, max_length=200)
    排序: int = Field(0, alias="sort")

    class Config:
        populate_by_name = True


class ChapterResponse(BaseModel):
    """章节响应（含课时列表）"""
    ID: int = Field(..., alias="id")
    课程ID: int = Field(..., alias="course_id")
    标题: str = Field(..., alias="title")
    排序: int = Field(0, alias="sort")
    课时列表: List[LessonResponse] = []
    labels: dict = {
        "ID": "id",
        "课程ID": "course_id",
        "标题": "title",
        "排序": "sort",
        "课时列表": "lessons"
    }

    class Config:
        populate_by_name = True


# ========== 课程 ==========

class CourseCreate(BaseModel):
    """创建课程"""
    标题: str = Field(..., alias="title", min_length=1, max_length=200)
    简介: Optional[str] = Field(None, alias="description")
    封面: Optional[str] = Field(None, alias="cover")
    分类ID: Optional[int] = Field(None, alias="category_id")
    讲师ID: Optional[int] = Field(None, alias="teacher_id")
    是否发布: bool = Field(False, alias="is_published")
    排序: int = Field(0, alias="sort")

    class Config:
        populate_by_name = True


class CourseUpdate(BaseModel):
    标题: Optional[str] = Field(None, alias="title")
    简介: Optional[str] = Field(None, alias="description")
    封面: Optional[str] = Field(None, alias="cover")
    分类ID: Optional[int] = Field(None, alias="category_id")
    讲师ID: Optional[int] = Field(None, alias="teacher_id")
    是否发布: Optional[bool] = Field(None, alias="is_published")
    排序: Optional[int] = Field(None, alias="sort")

    class Config:
        populate_by_name = True


class CourseResponse(BaseModel):
    """课程列表响应"""
    ID: int = Field(..., alias="id")
    标题: str = Field(..., alias="title")
    简介: Optional[str] = Field(None, alias="description")
    封面: Optional[str] = Field(None, alias="cover")
    分类ID: Optional[int] = Field(None, alias="category_id")
    分类名称: Optional[str] = None
    讲师ID: Optional[int] = Field(None, alias="teacher_id")
    讲师姓名: Optional[str] = None
    是否发布: bool = Field(False, alias="is_published")
    排序: int = Field(0, alias="sort")
    章节数量: int = 0
    课时数量: int = 0
    创建时间: Optional[str] = Field(None, alias="created_at")
    更新时间: Optional[str] = Field(None, alias="updated_at")
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "简介": "description",
        "封面": "cover",
        "分类ID": "category_id",
        "分类名称": "category_name",
        "讲师ID": "teacher_id",
        "讲师姓名": "teacher_name",
        "是否发布": "is_published",
        "排序": "sort",
        "章节数量": "chapter_count",
        "课时数量": "lesson_count",
        "创建时间": "created_at",
        "更新时间": "updated_at"
    }

    class Config:
        populate_by_name = True


class CourseDetailResponse(BaseModel):
    """课程详情（含章节和课时）"""
    ID: int = Field(..., alias="id")
    标题: str = Field(..., alias="title")
    简介: Optional[str] = Field(None, alias="description")
    封面: Optional[str] = Field(None, alias="cover")
    分类ID: Optional[int] = Field(None, alias="category_id")
    分类名称: Optional[str] = None
    讲师ID: Optional[int] = Field(None, alias="teacher_id")
    讲师姓名: Optional[str] = None
    是否发布: bool = Field(False, alias="is_published")
    排序: int = Field(0, alias="sort")
    章节列表: List[ChapterResponse] = []
    创建时间: Optional[str] = Field(None, alias="created_at")
    更新时间: Optional[str] = Field(None, alias="updated_at")
    labels: dict = {
        "ID": "id",
        "标题": "title",
        "简介": "description",
        "封面": "cover",
        "分类ID": "category_id",
        "分类名称": "category_name",
        "讲师ID": "teacher_id",
        "讲师姓名": "teacher_name",
        "是否发布": "is_published",
        "排序": "sort",
        "章节列表": "chapters",
        "创建时间": "created_at",
        "更新时间": "updated_at"
    }

    class Config:
        populate_by_name = True


# ========== 学习进度 ==========

class CourseProgressUpdate(BaseModel):
    """更新学习进度"""
    课时ID: int = Field(..., alias="lesson_id")
    进度: float = Field(0, alias="progress", ge=0, le=100)
    是否完成: bool = Field(False, alias="completed")
    视频位置: int = Field(0, alias="video_position", ge=0, description="视频播放位置(秒)")
    视频总时长: int = Field(0, alias="total_duration", ge=0, description="视频总时长(秒)")

    class Config:
        populate_by_name = True


class CourseProgressResponse(BaseModel):
    """学习进度响应"""
    ID: int
    用户ID: int
    课时ID: int
    课程ID: int
    进度: float = 0
    是否完成: bool = False
    更新时间: Optional[str] = None
    labels: dict = {
        "ID": "id",
        "用户ID": "user_id",
        "课时ID": "lesson_id",
        "课程ID": "course_id",
        "进度": "progress",
        "是否完成": "completed",
        "更新时间": "updated_at"
    }
