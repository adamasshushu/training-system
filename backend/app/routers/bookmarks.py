"""收藏与笔记路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.models.bookmark import CourseBookmark, LessonNote
from app.models.course import Course, Lesson, Chapter
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/bookmarks", tags=["收藏笔记"])


# ========== Pydantic ==========

class NoteCreate(BaseModel):
    课时ID: int = Field(..., alias="lesson_id")
    课程ID: int = Field(..., alias="course_id")
    内容: str = Field(..., alias="content", min_length=1)
    class Config: populate_by_name = True

class NoteUpdate(BaseModel):
    内容: str = Field(..., alias="content", min_length=1)
    class Config: populate_by_name = True


# ========== 收藏 ==========

@router.get("")
async def list_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """我的收藏列表"""
    query = select(CourseBookmark).where(
        CourseBookmark.user_id == current_user["id"]
    ).order_by(CourseBookmark.id.desc())

    result = await db.execute(query)
    all_items = result.scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    page_items = all_items[start:start + page_size]

    bookmark_list = []
    for b in page_items:
        c = (await db.execute(select(Course).where(Course.id == b.course_id))).scalar_one_or_none()
        if c:
            bookmark_list.append({
                "ID": b.id,
                "课程ID": b.course_id,
                "课程标题": c.title,
                "课程封面": c.cover,
                "收藏时间": str(b.created_at) if b.created_at else None,
            })

    return {
        "数据": bookmark_list,
        "共计": total,
        "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/{course_id}")
async def toggle_bookmark(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """切换收藏状态（如果已收藏则取消，否则收藏）"""
    c_result = await db.execute(select(Course).where(Course.id == course_id))
    if not c_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="课程不存在")

    result = await db.execute(
        select(CourseBookmark).where(
            CourseBookmark.user_id == current_user["id"],
            CourseBookmark.course_id == course_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()
        return {"收藏": False, "message": "已取消收藏", "labels": {"收藏": "bookmarked", "message": "消息"}}
    else:
        bookmark = CourseBookmark(user_id=current_user["id"], course_id=course_id)
        db.add(bookmark)
        await db.flush()
        return {"收藏": True, "ID": bookmark.id, "message": "已收藏", "labels": {"收藏": "bookmarked", "ID": "id", "message": "消息"}}


@router.get("/check/{course_id}")
async def check_bookmark(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """检查课程是否已收藏"""
    result = await db.execute(
        select(CourseBookmark).where(
            CourseBookmark.user_id == current_user["id"],
            CourseBookmark.course_id == course_id,
        )
    )
    return {"收藏": result.scalar_one_or_none() is not None, "labels": {"收藏": "bookmarked"}}


# ========== 笔记 ==========

@router.get("/notes")
async def list_notes(
    course_id: Optional[int] = Query(None, alias="course_id"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """我的笔记列表"""
    query = select(LessonNote).where(
        LessonNote.user_id == current_user["id"]
    )
    if course_id:
        query = query.where(LessonNote.course_id == course_id)
    query = query.order_by(LessonNote.id.desc())

    result = await db.execute(query)
    all_items = result.scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    page_items = all_items[start:start + page_size]

    note_list = []
    for n in page_items:
        le = (await db.execute(select(Lesson).where(Lesson.id == n.lesson_id))).scalar_one_or_none()
        c = (await db.execute(select(Course).where(Course.id == n.course_id))).scalar_one_or_none()
        note_list.append({
            "ID": n.id,
            "课时ID": n.lesson_id,
            "课时标题": le.title if le else "已删除",
            "课程ID": n.course_id,
            "课程标题": c.title if c else "已删除",
            "内容": n.content[:200] + ("..." if len(n.content) > 200 else ""),
            "内容全文": n.content,
            "更新时间": str(n.updated_at) if n.updated_at else None,
        })

    return {
        "数据": note_list,
        "共计": total,
        "页码": page, "每页数量": page_size,
        "labels": {"数据": "data", "共计": "total"}
    }


@router.post("/notes")
async def create_note(
    req: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建课时笔记"""
    le_result = await db.execute(
        select(Lesson).join(Chapter).where(
            Lesson.id == req.课时ID,
            Chapter.course_id == req.课程ID,
        )
    )
    if not le_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="课时不存在或不属于该课程")

    note = LessonNote(
        user_id=current_user["id"],
        lesson_id=req.课时ID,
        course_id=req.课程ID,
        content=req.内容,
    )
    db.add(note)
    await db.flush()
    return {"message": "笔记已保存", "ID": note.id, "labels": {"message": "消息", "ID": "id"}}


@router.put("/notes/{note_id}")
async def update_note(
    note_id: int,
    req: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新笔记"""
    result = await db.execute(
        select(LessonNote).where(
            LessonNote.id == note_id,
            LessonNote.user_id == current_user["id"],
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    note.content = req.内容
    await db.flush()
    return {"message": "笔记已更新", "labels": {"message": "消息"}}


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除笔记"""
    result = await db.execute(
        select(LessonNote).where(
            LessonNote.id == note_id,
            LessonNote.user_id == current_user["id"],
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    await db.delete(note)
    await db.flush()
    return {"message": "笔记已删除", "labels": {"message": "消息"}}


@router.get("/notes/lesson/{lesson_id}")
async def get_lesson_note(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单体课时的笔记"""
    result = await db.execute(
        select(LessonNote).where(
            LessonNote.user_id == current_user["id"],
            LessonNote.lesson_id == lesson_id,
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        return {"数据": None, "labels": {"数据": "data"}}
    return {
        "数据": {
            "ID": note.id, "内容": note.content,
            "更新时间": str(note.updated_at) if note.updated_at else None,
        },
        "labels": {"数据": "data"}
    }
