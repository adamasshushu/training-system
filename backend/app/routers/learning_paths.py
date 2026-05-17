"""学习路径路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.learning_path import LearningPath, LearningPathCourse, UserLearningPath
from app.models.course import Course, CourseProgress, Chapter, Lesson
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/learning-paths", tags=["学习路径"])


# ========== Pydantic ==========

class PathCourseCreate(BaseModel):
    课程ID: int = Field(..., alias="course_id")
    排序: int = Field(0, alias="sort")
    必修: bool = Field(True, alias="required")
    预估时长: float = Field(0, alias="estimated_hours")
    class Config: populate_by_name = True

class LearningPathCreate(BaseModel):
    名称: str = Field(..., alias="title", min_length=1, max_length=200)
    描述: Optional[str] = Field(None, alias="description")
    是否发布: bool = Field(False, alias="is_published")
    课程列表: list[PathCourseCreate] = Field(default_factory=list, alias="courses")
    排序: int = Field(0, alias="sort")
    class Config: populate_by_name = True

class LearningPathUpdate(BaseModel):
    名称: Optional[str] = Field(None, alias="title")
    描述: Optional[str] = Field(None, alias="description")
    是否发布: Optional[bool] = Field(None, alias="is_published")
    排序: Optional[int] = Field(None, alias="sort")
    class Config: populate_by_name = True


# ========== 管理员端 ==========

@router.get("")
async def list_paths(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """学习路径列表"""
    query = select(LearningPath).order_by(LearningPath.sort, LearningPath.id.desc())
    result = await db.execute(query)
    all_paths = result.scalars().all()
    total = len(all_paths)
    start = (page - 1) * page_size
    page_paths = all_paths[start:start + page_size]

    path_list = []
    for p in page_paths:
        course_ids = [pc.course_id for pc in p.courses]
        path_list.append({
            "ID": p.id,
            "名称": p.title,
            "描述": p.description,
            "是否发布": p.is_published,
            "排序": p.sort,
            "课程数量": len(p.courses),
            "课程ID列表": course_ids,
            "创建时间": str(p.created_at) if p.created_at else None,
        })

    return {
        "数据": path_list, "共计": total, "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total", "页码": "page", "每页数量": "page_size"}
    }


@router.post("")
async def create_path(
    req: LearningPathCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建学习路径"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")
    path = LearningPath(
        title=req.名称, description=req.描述,
        is_published=req.是否发布, created_by=current_user["id"], sort=req.排序,
    )
    db.add(path)
    await db.flush()

    for idx, pc in enumerate(req.课程列表):
        c_result = await db.execute(select(Course).where(Course.id == pc.课程ID))
        if not c_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"课程ID {pc.课程ID} 不存在")
        lpc = LearningPathCourse(
            path_id=path.id, course_id=pc.课程ID,
            sort=pc.排序 or idx, required=pc.必修, estimated_hours=pc.预估时长,
        )
        db.add(lpc)
    await db.flush()
    return {"message": "学习路径创建成功", "ID": path.id, "名称": path.title, "labels": {"message": "消息", "ID": "id", "名称": "title"}}


@router.get("/{path_id}")
async def get_path_detail(
    path_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """学习路径详情"""
    result = await db.execute(
        select(LearningPath).options(selectinload(LearningPath.courses)).where(LearningPath.id == path_id)
    )
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=404, detail="路径不存在")

    courses = []
    for pc in path.courses:
        c_result = await db.execute(select(Course).where(Course.id == pc.course_id))
        c = c_result.scalar_one_or_none()
        courses.append({
            "课程ID": pc.course_id,
            "排序": pc.sort,
            "必修": pc.required,
            "预估时长": pc.estimated_hours,
            "标题": c.title if c else "已删除",
        })
    return {
        "数据": {
            "ID": path.id, "名称": path.title, "描述": path.description,
            "是否发布": path.is_published, "排序": path.sort,
            "课程列表": courses,
            "创建时间": str(path.created_at) if path.created_at else None,
        },
        "labels": {"数据": "data", "课程列表": "courses"}
    }


@router.put("/{path_id}")
async def update_path(
    path_id: int,
    req: LearningPathUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新学习路径"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")
    result = await db.execute(select(LearningPath).where(LearningPath.id == path_id))
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=404, detail="路径不存在")
    if req.名称 is not None: path.title = req.名称
    if req.描述 is not None: path.description = req.描述
    if req.是否发布 is not None: path.is_published = req.是否发布
    if req.排序 is not None: path.sort = req.排序
    await db.flush()
    return {"message": "学习路径已更新", "labels": {"message": "消息"}}


@router.delete("/{path_id}")
async def delete_path(
    path_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除学习路径"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除")
    result = await db.execute(select(LearningPath).where(LearningPath.id == path_id))
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=404, detail="路径不存在")
    # cascading delete
    await db.delete(path)
    await db.flush()
    return {"message": "学习路径已删除", "labels": {"message": "消息"}}


@router.put("/{path_id}/courses")
async def update_path_courses(
    path_id: int,
    courses: list[PathCourseCreate],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新学习路径的课程列表"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")
    # 删除旧关联
    old_result = await db.execute(select(LearningPathCourse).where(LearningPathCourse.path_id == path_id))
    for old in old_result.scalars().all():
        await db.delete(old)
    # 添加新关联
    for idx, pc in enumerate(courses):
        lpc = LearningPathCourse(
            path_id=path_id, course_id=pc.课程ID,
            sort=pc.排序 or idx, required=pc.必修, estimated_hours=pc.预估时长,
        )
        db.add(lpc)
    await db.flush()
    return {"message": "课程列表已更新", "labels": {"message": "消息"}}


# ========== 学员端 ==========

@router.get("/my-paths")
async def list_my_paths(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """我的学习路径（学员端）"""
    # 查询所有已发布的路径
    result = await db.execute(
        select(LearningPath).options(selectinload(LearningPath.courses))
        .where(LearningPath.is_published == True)
        .order_by(LearningPath.sort)
    )
    paths = result.scalars().all()

    my_paths = []
    for p in paths:
        # 计算用户在该路径中的总体进度
        total_courses = len(p.courses)
        completed_courses = 0
        course_details = []

        for pc in p.courses:
            # 统计课程完成度
            total_lessons_result = await db.execute(
                select(Lesson).join(Chapter).where(Chapter.course_id == pc.course_id)
            )
            total_lessons = len(total_lessons_result.scalars().all())

            completed_result = await db.execute(
                select(CourseProgress).where(
                    CourseProgress.course_id == pc.course_id,
                    CourseProgress.user_id == current_user["id"],
                    CourseProgress.completed == True,
                )
            )
            completed = len(completed_result.scalars().all())

            c = (await db.execute(select(Course).where(Course.id == pc.course_id))).scalar_one_or_none()
            progress = round(completed / total_lessons * 100, 1) if total_lessons > 0 else 0

            if progress >= 100:
                completed_courses += 1

            course_details.append({
                "课程ID": pc.course_id,
                "标题": c.title if c else "已删除",
                "排序": pc.sort,
                "必修": pc.required,
                "总课时": total_lessons,
                "已完成课时": completed,
                "进度": progress,
            })

        my_paths.append({
            "ID": p.id,
            "名称": p.title,
            "描述": p.description,
            "总课程数": total_courses,
            "已完成课程": completed_courses,
            "总进度": round(completed_courses / total_courses * 100, 1) if total_courses > 0 else 0,
            "课程详情": course_details,
        })

    return {
        "数据": my_paths,
        "共计": len(my_paths),
        "labels": {"数据": "data", "共计": "total"}
    }
