"""知识图谱路由：自动从课程分类/标签构建知识关联"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.course import Course, CourseCategory, Chapter, Lesson
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/knowledge-graph", tags=["知识图谱"])


@router.get("")
async def get_knowledge_graph(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    自动构建知识图谱：
    - 节点: 课程分类、课程、课时
    - 边: 分类→课程、同分类关联、同标签关联
    """
    # 1. 节点: 课程分类
    cat_result = await db.execute(
        select(CourseCategory).where(CourseCategory.is_active == True).order_by(CourseCategory.sort)
    )
    categories = cat_result.scalars().all()

    nodes = []
    edges = []
    node_ids = set()

    # 分类节点
    for cat in categories:
        nid = f"cat_{cat.id}"
        nodes.append({
            "id": nid,
            "label": cat.name,
            "type": "category",
            "size": 15,
            "color": "#409EFF",
        })
        node_ids.add(nid)

        # 分类父子关系
        if cat.parent_id:
            parent_nid = f"cat_{cat.parent_id}"
            if parent_nid not in node_ids:
                # Add parent node
                p_result = await db.execute(select(CourseCategory).where(CourseCategory.id == cat.parent_id))
                p = p_result.scalar_one_or_none()
                if p:
                    nodes.append({
                        "id": parent_nid, "label": p.name, "type": "category",
                        "size": 15, "color": "#409EFF",
                    })
                    node_ids.add(parent_nid)
            edges.append({
                "source": parent_nid, "target": nid, "label": "包含",
                "color": "#409EFF", "width": 1,
            })

    # 2. 课程节点 + 分类→课程边
    course_result = await db.execute(
        select(Course).where(Course.is_published == True).order_by(Course.id)
    )
    courses = course_result.scalars().all()

    for c in courses:
        nid = f"course_{c.id}"
        # 计算课程完成度需要的数据作为size
        lesson_count = 0
        for ch in c.chapters:
            lesson_count += len(ch.lessons)

        nodes.append({
            "id": nid,
            "label": c.title[:20] + ("..." if len(c.title) > 20 else ""),
            "type": "course",
            "size": 25 + min(lesson_count * 2, 20),
            "color": "#67C23A",
            "full_title": c.title,
        })
        node_ids.add(nid)

        # 分类→课程边
        if c.category_id:
            cat_nid = f"cat_{c.category_id}"
            if cat_nid in node_ids:
                edges.append({
                    "source": cat_nid, "target": nid,
                    "label": "包含", "color": "#67C23A", "width": 2,
                })

    # 3. 课时节点 + 课程→课时边
    lesson_result = await db.execute(
        select(Lesson).join(Chapter).order_by(Lesson.id)
    )
    lessons = lesson_result.scalars().all()

    for le in lessons:
        nid = f"lesson_{le.id}"
        nodes.append({
            "id": nid,
            "label": le.title[:15] + ("..." if len(le.title) > 15 else ""),
            "type": "lesson",
            "size": 12,
            "color": "#E6A23C",
        })
        node_ids.add(nid)

        course_nid = f"course_{le.chapter.course_id}"
        if course_nid in node_ids:
            edges.append({
                "source": course_nid, "target": nid,
                "label": "课时", "color": "#E6A23C", "width": 1,
            })

    # 4. 同分类课程之间的关联边
    cat_courses = {}
    for c in courses:
        if c.category_id:
            if c.category_id not in cat_courses:
                cat_courses[c.category_id] = []
            cat_courses[c.category_id].append(c.id)

    for cat_id, course_ids in cat_courses.items():
        if len(course_ids) > 1:
            for i in range(len(course_ids) - 1):
                for j in range(i + 1, len(course_ids)):
                    if j - i <= 3:  # 限制边数量
                        edges.append({
                            "source": f"course_{course_ids[i]}",
                            "target": f"course_{course_ids[j]}",
                            "label": "相关课程",
                            "color": "#909399",
                            "width": 0.5,
                            "dashed": True,
                        })

    return {
        "数据": {
            "nodes": nodes,
            "edges": edges,
        },
        "统计": {
            "节点数": len(nodes),
            "边数": len(edges),
            "分类数": len(categories),
            "课程数": len(courses),
            "课时数": len(lessons),
        },
        "labels": {"数据": "data", "统计": "stats"}
    }
