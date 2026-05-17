"""课程管理路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.course import (
    Course, CourseCategory, Chapter, Lesson, CourseProgress
)
from app.utils.auth import get_current_user
from app.schemas.course import (
    CourseCategoryCreate, CourseCreate, CourseUpdate,
    ChapterCreate, LessonCreate, CourseProgressUpdate,
    CourseResponse, CourseDetailResponse, ChapterResponse, LessonResponse,
    CourseCategoryResponse
)

router = APIRouter(prefix="/api", tags=["课程管理"])


# ========== 课程分类 ==========

@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取课程分类列表（树形）"""
    result = await db.execute(
        select(CourseCategory)
        .where(CourseCategory.is_active == True)
        .order_by(CourseCategory.sort)
    )
    categories = result.scalars().all()
    cat_list = []
    for c in categories:
        course_count = await db.execute(
            select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons)).where(Course.category_id == c.id)
        )
        cat_list.append({
            "ID": c.id,
            "名称": c.name,
            "上级ID": c.parent_id,
            "排序": c.sort,
            "是否激活": c.is_active,
            "课程数量": len(course_count.scalars().all()),
        })

    # 构建树
    def build_tree(parent_id=None):
        tree = []
        for item in cat_list:
            if item["上级ID"] == parent_id:
                children = build_tree(item["ID"])
                item["子分类"] = children
                tree.append(item)
        return tree

    return {
        "数据": build_tree(),
        "共计": len(categories),
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/categories")
async def create_category(
    req: CourseCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建课程分类"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限创建分类")
    cat = CourseCategory(name=req.名称, parent_id=req.上级ID, sort=req.排序)
    db.add(cat)
    await db.flush()
    return {
        "message": "分类创建成功",
        "ID": cat.id,
        "名称": cat.name,
        "labels": {"message": "消息", "ID": "id", "名称": "name"}
    }


# ========== 课程列表 ==========

@router.get("/courses")
async def list_courses(
    category_id: Optional[int] = Query(None, alias="category_id"),
    keyword: Optional[str] = Query(None, alias="keyword"),
    is_published: Optional[bool] = Query(None, alias="is_published"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """课程列表（管理端）"""
    query = select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons))
    if category_id:
        query = query.where(Course.category_id == category_id)
    if keyword:
        query = query.where(Course.title.contains(keyword))
    if is_published is not None:
        query = query.where(Course.is_published == is_published)
    query = query.order_by(Course.sort, Course.id.desc())

    result = await db.execute(query)
    courses = result.scalars().all()

    total = len(courses)
    start = (page - 1) * page_size
    page_courses = courses[start:start + page_size]

    course_list = []
    for c in page_courses:
        cat_name = None
        if c.category_id:
            cat_result = await db.execute(
                select(CourseCategory).where(CourseCategory.id == c.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                cat_name = cat.name
        teacher_name = None
        if c.teacher_id:
            t_result = await db.execute(select(User).where(User.id == c.teacher_id))
            t = t_result.scalar_one_or_none()
            if t:
                teacher_name = t.real_name
        chapter_count = len(c.chapters)
        lesson_count = sum(len(ch.lessons) for ch in c.chapters)
        course_list.append({
            "ID": c.id,
            "标题": c.title,
            "简介": c.description,
            "封面": c.cover,
            "分类ID": c.category_id,
            "分类名称": cat_name,
            "讲师ID": c.teacher_id,
            "讲师姓名": teacher_name,
            "是否发布": c.is_published,
            "排序": c.sort,
            "章节数量": chapter_count,
            "课时数量": lesson_count,
            "创建时间": str(c.created_at) if c.created_at else None,
            "更新时间": str(c.updated_at) if c.updated_at else None,
        })

    return {
        "数据": course_list,
        "共计": total,
        "页码": page,
        "每页数量": page_size,
        "labels": {
            "数据": "data", "共计": "total",
            "页码": "page", "每页数量": "page_size"
        }
    }


@router.get("/courses/student")
async def list_student_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """学员端课程列表（仅已发布课程）"""
    result = await db.execute(
        select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons))
        .where(Course.is_published == True)
        .order_by(Course.sort, Course.id.desc())
    )
    courses = result.scalars().all()
    course_list = []
    for c in courses:
        cat_name = None
        if c.category_id:
            cat_result = await db.execute(
                select(CourseCategory).where(CourseCategory.id == c.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                cat_name = cat.name
        teacher_name = None
        if c.teacher_id:
            t_result = await db.execute(select(User).where(User.id == c.teacher_id))
            t = t_result.scalar_one_or_none()
            if t:
                teacher_name = t.real_name
        course_list.append({
            "ID": c.id,
            "标题": c.title,
            "简介": c.description,
            "封面": c.cover,
            "分类名称": cat_name,
            "讲师姓名": teacher_name,
        })
    return {
        "数据": course_list,
        "共计": len(course_list),
        "labels": {"数据": "data", "共计": "total"}
    }


# ========== 课程详情 ==========

@router.get("/courses/{course_id}")
async def get_course_detail(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取课程详情（含章节和课时）"""
    result = await db.execute(select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons)).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    cat_name = None
    if course.category_id:
        cat_result = await db.execute(
            select(CourseCategory).where(CourseCategory.id == course.category_id)
        )
        cat = cat_result.scalar_one_or_none()
        if cat:
            cat_name = cat.name
    teacher_name = None
    if course.teacher_id:
        t_result = await db.execute(select(User).where(User.id == course.teacher_id))
        t = t_result.scalar_one_or_none()
        if t:
            teacher_name = t.real_name

    chapters = []
    for ch in course.chapters:
        lessons = []
        for le in ch.lessons:
            lessons.append({
                "ID": le.id,
                "章节ID": le.chapter_id,
                "标题": le.title,
                "课时类型": le.lesson_type,
                "图文内容": le.content_text,
                "文件地址": le.file_url,
                "时长": le.duration,
                "排序": le.sort,
                "是否免费": le.is_free,
            })
        chapters.append({
            "ID": ch.id,
            "课程ID": ch.course_id,
            "标题": ch.title,
            "排序": ch.sort,
            "课时列表": lessons,
        })

    return {
        "数据": {
            "ID": course.id,
            "标题": course.title,
            "简介": course.description,
            "封面": course.cover,
            "分类ID": course.category_id,
            "分类名称": cat_name,
            "讲师ID": course.teacher_id,
            "讲师姓名": teacher_name,
            "是否发布": course.is_published,
            "排序": course.sort,
            "章节列表": chapters,
            "创建时间": str(course.created_at) if course.created_at else None,
            "更新时间": str(course.updated_at) if course.updated_at else None,
        },
        "labels": {
            "ID": "id", "标题": "title", "简介": "description",
            "分类ID": "category_id", "分类名称": "category_name",
            "讲师ID": "teacher_id", "讲师姓名": "teacher_name",
            "是否发布": "is_published", "章节列表": "chapters"
        }
    }


# ========== 课程CRUD ==========

@router.post("/courses")
async def create_course(
    req: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建课程"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限创建课程")
    course = Course(
        title=req.标题,
        description=req.简介,
        cover=req.封面,
        category_id=req.分类ID,
        teacher_id=req.讲师ID or current_user.get("id"),
        is_published=req.是否发布,
        sort=req.排序,
    )
    db.add(course)
    await db.flush()
    return {
        "message": "课程创建成功",
        "ID": course.id,
        "标题": course.title,
        "labels": {"message": "消息", "ID": "id", "标题": "title"}
    }


@router.put("/courses/{course_id}")
async def update_course(
    course_id: int,
    req: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新课程"""
    result = await db.execute(select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons)).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if current_user.get("角色") not in ("admin",) and course.teacher_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="无权限修改该课程")
    if req.标题 is not None:
        course.title = req.标题
    if req.简介 is not None:
        course.description = req.简介
    if req.封面 is not None:
        course.cover = req.封面
    if req.分类ID is not None:
        course.category_id = req.分类ID
    if req.讲师ID is not None:
        course.teacher_id = req.讲师ID
    if req.是否发布 is not None:
        course.is_published = req.是否发布
    if req.排序 is not None:
        course.sort = req.排序
    await db.flush()
    return {"message": "课程更新成功", "labels": {"message": "消息"}}


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除课程"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除课程")
    result = await db.execute(select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons)).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    await db.delete(course)
    await db.flush()
    return {"message": "课程已删除", "labels": {"message": "消息"}}


# ========== 章节 ==========

@router.post("/courses/{course_id}/chapters")
async def create_chapter(
    course_id: int,
    req: ChapterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建章节"""
    result = await db.execute(select(Course).options(selectinload(Course.chapters).selectinload(Chapter.lessons)).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if current_user.get("角色") not in ("admin",) and course.teacher_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="无权限")
    chapter = Chapter(course_id=course_id, title=req.标题, sort=req.排序)
    db.add(chapter)
    await db.flush()
    return {
        "message": "章节创建成功",
        "ID": chapter.id,
        "标题": chapter.title,
        "labels": {"message": "消息", "ID": "id", "标题": "title"}
    }


# ========== 课时 ==========

@router.post("/courses/{course_id}/lessons")
async def create_lesson(
    course_id: int,
    req: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建课时"""
    result = await db.execute(select(Chapter).where(
        Chapter.id == req.章节ID, Chapter.course_id == course_id
    ))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="章节不存在或不属于该课程")
    lesson = Lesson(
        chapter_id=req.章节ID,
        title=req.标题,
        lesson_type=req.课时类型,
        content_text=req.图文内容,
        file_url=req.文件地址,
        duration=req.时长,
        sort=req.排序,
        is_free=req.是否免费,
    )
    db.add(lesson)
    await db.flush()
    return {
        "message": "课时创建成功",
        "ID": lesson.id,
        "标题": lesson.title,
        "labels": {"message": "消息", "ID": "id", "标题": "title"}
    }


# ========== 学习进度 ==========

@router.post("/courses/{course_id}/progress")
async def update_progress(
    course_id: int,
    req: CourseProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新学习进度"""
    # 检查课时是否属于该课程
    lesson_result = await db.execute(
        select(Lesson).join(Chapter).where(
            Lesson.id == req.课时ID,
            Chapter.course_id == course_id,
        )
    )
    if not lesson_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="课时不存在或不属于该课程")
    # 查找或创建进度记录
    prog_result = await db.execute(
        select(CourseProgress).where(
            CourseProgress.user_id == current_user["id"],
            CourseProgress.lesson_id == req.课时ID,
            CourseProgress.course_id == course_id,
        )
    )
    progress = prog_result.scalar_one_or_none()
    if not progress:
        progress = CourseProgress(
            user_id=current_user["id"],
            lesson_id=req.课时ID,
            course_id=course_id,
        )
        db.add(progress)
    progress.progress = req.进度
    progress.completed = req.是否完成
    await db.flush()
    return {
        "message": "进度已更新",
        "进度": progress.progress,
        "是否完成": progress.completed,
        "labels": {"message": "消息", "进度": "progress", "是否完成": "completed"}
    }
