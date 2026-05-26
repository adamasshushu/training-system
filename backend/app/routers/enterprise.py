"""企业平台管理路由：钉钉/飞书/企微配置、同步、通知"""
import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.enterprise import EnterpriseConfig
from app.models.user import User
from app.models.sync_log import SyncLog
from app.models.task import TrainingTask, TaskAssignment
from app.utils.auth import get_current_user
from app.utils.enterprise_connector import get_connector
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/enterprise", tags=["企业平台"])


# ========== Pydantic ==========

class PlatformConfigUpdate(BaseModel):
    """平台配置更新"""
    启用: bool = Field(False, alias="is_enabled")
    配置: dict = Field(default_factory=dict, alias="config")
    class Config: populate_by_name = True

class SyncRequest(BaseModel):
    """同步请求"""
    平台: str = Field(..., alias="platform", pattern="^(dingtalk|feishu|wecom|ldap)$")
    class Config: populate_by_name = True

class NotifyRequest(BaseModel):
    """通知请求"""
    任务ID: int = Field(..., alias="task_id")
    平台: Optional[str] = Field(None, alias="platform")
    class Config: populate_by_name = True


# ========== 配置管理 ==========

@router.get("/configs")
async def list_enterprise_configs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取所有企业平台配置（隐藏密钥）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看")

    result = await db.execute(select(EnterpriseConfig).order_by(EnterpriseConfig.id))
    configs = result.scalars().all()

    config_list = []
    platform_names = {"dingtalk": "钉钉", "feishu": "飞书", "wecom": "企业微信", "ldap": "LDAP/AD"}
    for c in configs:
        config_dict = {}
        if c.config_json:
            try:
                full_config = json.loads(c.config_json)
                # 隐藏密钥字段
                for k, v in full_config.items():
                    if "secret" in k.lower() or "key" in k.lower():
                        config_dict[k] = v[:4] + "****" if len(v) > 4 else "****"
                    else:
                        config_dict[k] = v
            except (json.JSONDecodeError, TypeError):
                config_dict = {"raw": str(c.config_json)[:50]}

        config_list.append({
            "ID": c.id,
            "平台": c.platform,
            "平台名称": platform_names.get(c.platform, c.platform),
            "启用": c.is_enabled,
            "配置": config_dict,
        })

    return {"数据": config_list, "labels": {"数据": "data"}}


@router.get("/configs/{platform}")
async def get_platform_config(
    platform: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取单个平台配置"""
    result = await db.execute(
        select(EnterpriseConfig).where(EnterpriseConfig.platform == platform)
    )
    config = result.scalar_one_or_none()
    if not config:
        return {"数据": {"平台": platform, "启用": False, "配置": {}}, "labels": {"数据": "data"}}

    full_config = {}
    if config.config_json:
        try:
            full_config = json.loads(config.config_json)
        except (json.JSONDecodeError, TypeError):
            full_config = {}

    return {
        "数据": {
            "ID": config.id,
            "平台": config.platform,
            "启用": config.is_enabled,
            "配置": full_config,  # 管理员页面需要看到完整密钥才能修改
        },
        "labels": {"数据": "data"}
    }


@router.put("/configs/{platform}")
async def update_platform_config(
    platform: str,
    req: PlatformConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新平台配置"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可配置")

    result = await db.execute(
        select(EnterpriseConfig).where(EnterpriseConfig.platform == platform)
    )
    config = result.scalar_one_or_none()

    if config:
        config.is_enabled = req.启用
        config.config_json = json.dumps(req.配置, ensure_ascii=False)
    else:
        config = EnterpriseConfig(
            platform=platform,
            is_enabled=req.启用,
            config_json=json.dumps(req.配置, ensure_ascii=False),
        )
        db.add(config)

    await db.flush()
    return {"message": f"{platform} 配置已保存", "labels": {"message": "消息"}}


# ========== 连接测试 ==========

@router.post("/test-connection/{platform}")
async def test_platform_connection(
    platform: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """测试平台连接"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可测试")

    result = await db.execute(
        select(EnterpriseConfig).where(EnterpriseConfig.platform == platform)
    )
    config = result.scalar_one_or_none()
    if not config or not config.config_json:
        raise HTTPException(status_code=400, detail="请先保存配置")

    connector = get_connector(platform, config.config_json)
    if not connector:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")

    try:
        success, message = await connector.test_connection()
        return {"success": success, "message": message, "labels": {"message": "消息"}}
    except Exception as e:
        return {"success": False, "message": str(e), "labels": {"message": "消息"}}


# ========== 组织同步 ==========

@router.post("/sync")
async def sync_organization(
    req: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """同步组织架构（从企业平台拉取部门/员工）"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可触发同步")

    result = await db.execute(
        select(EnterpriseConfig).where(EnterpriseConfig.platform == req.平台)
    )
    config = result.scalar_one_or_none()
    if not config or not config.is_enabled:
        raise HTTPException(status_code=400, detail=f"{req.平台} 未启用或未配置")

    connector = get_connector(req.平台, config.config_json)
    if not connector:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {req.平台}")

    try:
        stats = await connector.sync_organization(db)
        
        # 记录同步日志
        log = SyncLog(
            platform=req.平台,
            status="success" if not stats.get("error") else "error",
            ous_synced=stats.get("ous_synced", 0),
            users_added=stats.get("users_added", 0),
            users_updated=stats.get("users_updated", 0),
            users_skipped=stats.get("users_skipped", 0),
            errors=json.dumps(stats.get("errors", []), ensure_ascii=False),
            operator=current_user.get("用户名", "unknown"),
        )
        db.add(log)
        await db.commit()
        return {
            "message": "同步完成",
            "数据": stats,
            "labels": {"message": "消息", "数据": "stats"}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


# ========== 同步日志 ==========

@router.get("/sync-logs")
async def get_sync_logs(
    platform: str = Query(None, alias="platform"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取同步历史日志"""
    if current_user.get("角色") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看")

    query = select(SyncLog).order_by(SyncLog.created_at.desc())
    if platform:
        query = query.where(SyncLog.platform == platform)
    query = query.limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    log_list = []
    for l in logs:
        errors_list = []
        if l.errors:
            try:
                errors_list = json.loads(l.errors)
            except (json.JSONDecodeError, TypeError):
                errors_list = [l.errors]

        log_list.append({
            "ID": l.id,
            "平台": l.platform,
            "状态": l.status,
            "部门数": l.ous_synced,
            "新增用户": l.users_added,
            "更新用户": l.users_updated,
            "跳过用户": l.users_skipped,
            "错误": errors_list,
            "操作人": l.operator,
            "时间": str(l.created_at),
        })

    return {
        "数据": log_list,
        "共计": len(log_list),
        "labels": {"数据": "data", "共计": "total"},
    }


# ========== 消息通知 ==========

@router.post("/notify")
async def notify_task_assignment(
    req: NotifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """发送培训任务通知到企业平台"""
    if current_user.get("角色") not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="无权限")

    # 获取任务信息
    result = await db.execute(
        select(TrainingTask).where(TrainingTask.id == req.任务ID)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取所有被指派的用户
    assignment_result = await db.execute(
        select(TaskAssignment).where(TaskAssignment.task_id == req.任务ID)
    )
    assignments = assignment_result.scalars().all()

    user_ids = []
    for a in assignments:
        if a.assignee_type == "user":
            user_ids.append(a.assignee_id)
        elif a.assignee_type == "department":
            dept_users = await db.execute(
                select(User).where(User.department_id == a.assignee_id, User.is_active == True)
            )
            for u in dept_users.scalars().all():
                user_ids.append(u.id)

    # 获取开启的平台
    platforms_to_notify = []
    if req.平台:
        platforms_to_notify = [req.平台]
    else:
        conf_result = await db.execute(
            select(EnterpriseConfig).where(EnterpriseConfig.is_enabled == True)
        )
        platforms_to_notify = [c.platform for c in conf_result.scalars().all()]

    if not platforms_to_notify:
        raise HTTPException(status_code=400, detail="未找到已启用的企业平台")

    results = {}
    for platform in platforms_to_notify:
        conf_result = await db.execute(
            select(EnterpriseConfig).where(
                EnterpriseConfig.platform == platform,
                EnterpriseConfig.is_enabled == True,
            )
        )
        config = conf_result.scalar_one_or_none()
        if not config:
            continue

        connector = get_connector(platform, config.config_json)
        if not connector:
            continue

        # 构建消息内容
        deadline_str = f"\n> 截止日期: {task.deadline}" if task.deadline else ""
        content = f"""**📢 新的培训任务**
> **{task.title}**{deadline_str}
> {task.description or ''}
> 请登录培训系统查看详情并完成学习。"""

        try:
            # 发送给所有被指派的用户
            notify_user_ids = [str(uid) for uid in user_ids]
            if notify_user_ids:
                result = await connector.send_message(notify_user_ids, content)
                results[platform] = {"sent": len(notify_user_ids), "result": result}
        except Exception as e:
            results[platform] = {"error": str(e)}

    return {
        "message": "通知已发送",
        "数据": results,
        "labels": {"message": "消息", "数据": "results"}
    }
