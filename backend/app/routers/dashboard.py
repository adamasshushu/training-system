"""学员仪表盘：甘特图数据 + 学习概览"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.task import TrainingTask, TaskAssignment, TaskCourse, TaskExam
from app.models.course import Course, CourseProgress, Chapter, Lesson
from app.models.exam import Exam, ExamResult
from app.models.learning_path import LearningPath, LearningPathCourse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/gantt")
async def get_student_gantt(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """学员端：甘特图时间线数据"""
    user_id = current_user["id"]

    # 1. 获取与我相关的任务
    result = await db.execute(
        select(TaskAssignment).where(
            (TaskAssignment.assignee_type == "user") & (TaskAssignment.assignee_id == user_id)
        )
    )
    user_assignments = result.scalars().all()

    u_result = await db.execute(select(User).where(User.id == user_id))
    user = u_result.scalar_one_or_none()
    dept_assignments = []
    if user and user.department_id:
        result = await db.execute(
            select(TaskAssignment).where(
                (TaskAssignment.assignee_type == "department") &
                (TaskAssignment.assignee_id == user.department_id)
            )
        )
        dept_assignments = result.scalars().all()

    task_ids = set()
    for a in user_assignments + dept_assignments:
        task_ids.add(a.task_id)

    timeline_items = []

    for tid in task_ids:
        t_result = await db.execute(
            select(TrainingTask).where(TrainingTask.id == tid, TrainingTask.is_published == True)
        )
        task = t_result.scalar_one_or_none()
        if not task:
            continue

        # 统计任务进度
        tc_result = await db.execute(
            select(TaskCourse).where(TaskCourse.task_id == tid)
        )
        task_courses = tc_result.scalars().all()

        total_items = 0
        done_items = 0

        for tc in task_courses:
            total_items += 1
            total_lessons_result = await db.execute(
                select(Lesson).join(Chapter).where(Chapter.course_id == tc.course_id)
            )
            total_lessons = len(total_lessons_result.scalars().all())

            completed_result = await db.execute(
                select(CourseProgress).where(
                    CourseProgress.course_id == tc.course_id,
                    CourseProgress.user_id == user_id,
                    CourseProgress.completed == True,
                )
            )
            completed = len(completed_result.scalars().all())

            if total_lessons > 0 and completed >= total_lessons:
                done_items += 1

        te_result = await db.execute(
            select(TaskExam).where(TaskExam.task_id == tid)
        )
        task_exams = te_result.scalars().all()
        for te in task_exams:
            total_items += 1
            er_result = await db.execute(
                select(ExamResult).where(
                    ExamResult.exam_id == te.exam_id,
                    ExamResult.user_id == user_id,
                    ExamResult.status == "passed",
                )
            )
            if er_result.scalar_one_or_none():
                done_items += 1

        progress_pct = round(done_items / total_items * 100, 1) if total_items > 0 else 0

        # 确定状态颜色
        deadline = task.deadline
        now = datetime.now(timezone.utc)
        status = "进行中"
        color = "#409EFF"  # blue
        if deadline and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if progress_pct >= 100:
            status = "已完成"
            color = "#67C23A"  # green
        elif deadline and deadline < now:
            status = "已超期"
            color = "#F56C6C"  # red
        elif deadline and (deadline - now).days <= 3:
            status = "即将到期"
            color = "#E6A23C"  # orange

        timeline_items.append({
            "ID": task.id,
            "类型": "task",
            "标题": task.title,
            "截止日期": str(task.deadline) if task.deadline else None,
            "当前进度": progress_pct,
            "已完成数": done_items,
            "总项目数": total_items,
            "状态": status,
            "颜色": color,
        })

    # 2. 学习路径也加入甘特图（展示课程进度）
    path_result = await db.execute(
        select(LearningPath).where(LearningPath.is_published == True).order_by(LearningPath.sort)
    )
    paths = path_result.scalars().all()

    for p in paths:
        pc_result = await db.execute(
            select(LearningPathCourse).where(LearningPathCourse.path_id == p.id).order_by(LearningPathCourse.sort)
        )
        pc_list = pc_result.scalars().all()

        total_courses = len(pc_list)
        completed_courses = 0

        for pc in pc_list:
            total_lessons_result = await db.execute(
                select(Lesson).join(Chapter).where(Chapter.course_id == pc.course_id)
            )
            total_lessons = len(total_lessons_result.scalars().all())
            completed_result = await db.execute(
                select(CourseProgress).where(
                    CourseProgress.course_id == pc.course_id,
                    CourseProgress.user_id == user_id,
                    CourseProgress.completed == True,
                )
            )
            completed = len(completed_result.scalars().all())
            if total_lessons > 0 and completed >= total_lessons:
                completed_courses += 1

        progress_pct = round(completed_courses / total_courses * 100, 1) if total_courses > 0 else 0

        timeline_items.append({
            "ID": p.id,
            "类型": "learning_path",
            "标题": f"📚 {p.title}",
            "截止日期": None,
            "当前进度": progress_pct,
            "已完成数": completed_courses,
            "总项目数": total_courses,
            "状态": progress_pct >= 100 and "已完成" or "学习中",
            "颜色": progress_pct >= 100 and "#67C23A" or "#909399",
        })

    return {
        "数据": timeline_items,
        "共计": len(timeline_items),
        "labels": {"数据": "data", "共计": "total"}
    }
