"""
企业平台连接器：钉钉、飞书、企业微信统一接口

架构：
- 每个平台实现一个 Connector 类
- 通过 get_connector(platform) 工厂方法获取实例
- 提供 sync_organization() 同步组织架构
- 提供 send_message() 发送消息通知
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PlatformConnector(ABC):
    """平台连接器基类"""

    def __init__(self, config: dict):
        self.config = config
        self._client = None

    @abstractmethod
    async def sync_organization(self, db: AsyncSession) -> dict:
        """同步组织架构，返回 {departments: [...], users: [...], stats: {...}}"""
        pass

    @abstractmethod
    async def send_message(self, user_ids: list[str], content: str) -> dict:
        """发送消息通知"""
        pass

    @abstractmethod
    async def get_access_token(self) -> str:
        """获取访问令牌"""
        pass


# ========================================================================
# 钉钉连接器
# ========================================================================

class DingTalkConnector(PlatformConnector):
    """钉钉连接器"""

    async def get_access_token(self) -> str:
        import httpx
        app_key = self.config.get("app_key")
        app_secret = self.config.get("app_secret")
        if not app_key or not app_secret:
            raise ValueError("钉钉配置缺失: app_key/app_secret")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oapi.dingtalk.com/gettoken",
                params={"appkey": app_key, "appsecret": app_secret}
            )
            data = resp.json()
            if data.get("errcode") != 0:
                raise Exception(f"钉钉token获取失败: {data}")
            return data["access_token"]

    async def sync_organization(self, db: AsyncSession) -> dict:
        from app.models.department import Department
        from app.models.user import User
        from app.utils.auth import get_password_hash
        from sqlalchemy import select

        token = await self.get_access_token()
        stats = {"departments_added": 0, "users_added": 0, "users_updated": 0}

        async with httpx.AsyncClient() as client:
            # 1. 获取部门列表
            dept_resp = await client.post(
                "https://oapi.dingtalk.com/topapi/v2/department/listsub",
                params={"access_token": token},
                json={"dept_id": 1}
            )
            dept_data = dept_resp.json()

            if dept_data.get("errcode") == 0:
                dept_list = dept_data.get("result", [])
            else:
                # fallback: 获取单个部门树
                dept_list = []
                tree_resp = await client.post(
                    "https://oapi.dingtalk.com/topapi/v2/department/list",
                    params={"access_token": token},
                    json={"dept_id": 1}
                )
                tree_data = tree_resp.json()
                dept_list = self._flatten_dept_tree(tree_data.get("result", []))
                if not dept_list:
                    dept_list = [{"dept_id": 1, "name": self.config.get("corp_name", "企业"), "parent_id": 0}]

            # 同步部门
            dept_id_map = {0: None}
            for dd in dept_list:
                external_id = str(dd.get("dept_id"))
                parent_external_id = str(dd.get("parent_id", 0))

                result = await db.execute(
                    select(Department).where(Department.name == dd.get("name"))
                )
                dept = result.scalar_one_or_none()
                if not dept:
                    dept = Department(
                        name=dd.get("name", "未知部门"),
                        parent_id=dept_id_map.get(parent_external_id),
                        sort=dd.get("order", 0),
                        is_active=True,
                    )
                    db.add(dept)
                    await db.flush()
                    stats["departments_added"] += 1

                dept_id_map[external_id] = dept.id

            # 2. 获取员工列表
            cursor = 0
            has_more = True
            while has_more:
                user_resp = await client.post(
                    "https://oapi.dingtalk.com/topapi/v2/user/list",
                    params={"access_token": token},
                    json={"dept_id": 1, "cursor": cursor, "size": 100}
                )
                user_data = user_resp.json()
                if user_data.get("errcode") == 0:
                    user_list = user_data.get("result", {}).get("list", [])
                    for u in user_list:
                        username = u.get("userid") or u.get("mobile", "")
                        if not username:
                            continue
                        result = await db.execute(
                            select(User).where(User.username == username[:50])
                        )
                        user = result.scalar_one_or_none()
                        if user:
                            user.real_name = u.get("name", user.real_name)
                            user.email = u.get("email") or user.email
                            user.phone = u.get("mobile") or user.phone
                            dept_ids = u.get("dept_id_list", [])
                            if dept_ids:
                                ext_id = str(dept_ids[0])
                                if ext_id in dept_id_map:
                                    user.department_id = dept_id_map[ext_id]
                            stats["users_updated"] += 1
                        else:
                            dept_ids = u.get("dept_id_list", [])
                            dept_id = dept_id_map.get(str(dept_ids[0])) if dept_ids else None
                            user = User(
                                username=username[:50],
                                real_name=u.get("name", ""),
                                email=u.get("email"),
                                phone=u.get("mobile"),
                                password_hash=get_password_hash("123456"),
                                role="student",
                                department_id=dept_id,
                                is_active=True,
                            )
                            db.add(user)
                            stats["users_added"] += 1

                    has_more = user_data.get("result", {}).get("has_more", False)
                    cursor = user_data.get("result", {}).get("next_cursor", 0)
                else:
                    has_more = False

        return {"platform": "dingtalk", **stats}

    def _flatten_dept_tree(self, tree, parent_id=0):
        result = []
        for item in tree:
            result.append({
                "dept_id": item.get("dept_id"),
                "name": item.get("name"),
                "parent_id": parent_id,
                "order": item.get("order", 0),
            })
            children = item.get("children", [])
            if children:
                result.extend(self._flatten_dept_tree(children, item.get("dept_id")))
        return result

    async def send_message(self, user_ids: list[str], content: str) -> dict:
        token = await self.get_access_token()
        agent_id = self.config.get("agent_id")
        if not agent_id:
            raise ValueError("钉钉配置缺失: agent_id")

        import httpx
        async with httpx.AsyncClient() as client:
            results = []
            for uid in user_ids:
                resp = await client.post(
                    "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2",
                    params={"access_token": token},
                    json={
                        "agent_id": int(agent_id),
                        "userid_list": uid,
                        "msg": {
                            "msgtype": "markdown",
                            "markdown": {"title": "培训通知", "text": content}
                        }
                    }
                )
                results.append(resp.json())
        return {"results": results}


# ========================================================================
# 飞书连接器
# ========================================================================

class FeishuConnector(PlatformConnector):
    """飞书连接器"""

    async def get_tenant_token(self) -> str:
        import httpx
        app_id = self.config.get("app_id")
        app_secret = self.config.get("app_secret")
        if not app_id or not app_secret:
            raise ValueError("飞书配置缺失: app_id/app_secret")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": app_id, "app_secret": app_secret}
            )
            data = resp.json()
            if data.get("code") != 0:
                raise Exception(f"飞书token获取失败: {data}")
            return data["tenant_access_token"]

    async def get_access_token(self) -> str:
        return await self.get_tenant_token()

    async def sync_organization(self, db: AsyncSession) -> dict:
        from app.models.department import Department
        from app.models.user import User
        from app.utils.auth import get_password_hash
        from sqlalchemy import select

        token = await self.get_access_token()
        stats = {"departments_added": 0, "users_added": 0, "users_updated": 0}

        import httpx
        async with httpx.AsyncClient() as client:
            # 1. 获取部门
            dept_resp = await client.get(
                "https://open.feishu.cn/open-apis/contact/v3/departments",
                params={"page_size": 50},
                headers={"Authorization": f"Bearer {token}"}
            )
            dept_data = dept_resp.json()
            dept_list = dept_data.get("data", {}).get("items", [])

            dept_id_map = {"0": None}
            for dd in dept_list:
                dept_id_map[dd.get("open_department_id", dd.get("department_id"))] = None

            # First pass: create departments
            for dd in dept_list:
                ext_id = dd.get("open_department_id") or dd.get("department_id")
                parent_ext_id = dd.get("parent_department_id", "0")

                result = await db.execute(
                    select(Department).where(Department.name == dd.get("name"))
                )
                dept = result.scalar_one_or_none()
                if not dept:
                    dept = Department(
                        name=dd.get("name", "未知"),
                        parent_id=dept_id_map.get(parent_ext_id),
                        sort=dd.get("sort", 0),
                        is_active=True,
                    )
                    db.add(dept)
                    await db.flush()
                    stats["departments_added"] += 1
                dept_id_map[ext_id] = dept.id

            # 2. 获取员工
            page_token = None
            while True:
                params = {"page_size": 100}
                if page_token:
                    params["page_token"] = page_token

                user_resp = await client.get(
                    "https://open.feishu.cn/open-apis/contact/v3/users",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                user_data = user_resp.json()
                if user_data.get("code") != 0:
                    break

                user_items = user_data.get("data", {}).get("items", [])
                for u in user_items:
                    username = u.get("user_id") or u.get("mobile", "") or u.get("email", "")
                    if not username:
                        continue
                    result = await db.execute(
                        select(User).where(User.username == str(username)[:50])
                    )
                    user = result.scalar_one_or_none()
                    dept_ids = u.get("department_ids", [])
                    dept_id = dept_id_map.get(dept_ids[0]) if dept_ids else None

                    if user:
                        user.real_name = u.get("name", user.real_name)
                        user.email = u.get("email") or user.email
                        user.phone = u.get("mobile") or user.phone
                        if dept_id: user.department_id = dept_id
                        stats["users_updated"] += 1
                    else:
                        user = User(
                            username=str(username)[:50],
                            real_name=u.get("name", ""),
                            email=u.get("email"),
                            phone=u.get("mobile"),
                            password_hash=get_password_hash("123456"),
                            role="student",
                            department_id=dept_id,
                            is_active=True,
                        )
                        db.add(user)
                        stats["users_added"] += 1

                has_more = user_data.get("data", {}).get("has_more", False)
                if not has_more:
                    break
                page_token = user_data.get("data", {}).get("page_token")

        return {"platform": "feishu", **stats}

    async def send_message(self, user_ids: list[str], content: str) -> dict:
        token = await self.get_access_token()
        import httpx
        async with httpx.AsyncClient() as client:
            results = []
            for uid in user_ids:
                resp = await client.post(
                    "https://open.feishu.cn/open-apis/im/v1/messages",
                    params={"receive_id_type": "open_id"},
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "receive_id": uid,
                        "msg_type": "text",
                        "content": json.dumps({"text": content})
                    }
                )
                results.append(resp.json())
        return {"results": results}


# ========================================================================
# 企业微信连接器
# ========================================================================

class WeComConnector(PlatformConnector):
    """企业微信连接器"""

    async def get_access_token(self) -> str:
        import httpx
        corp_id = self.config.get("corp_id")
        corp_secret = self.config.get("corp_secret")
        if not corp_id or not corp_secret:
            raise ValueError("企微配置缺失: corp_id/corp_secret")

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
                params={"corpid": corp_id, "corpsecret": corp_secret}
            )
            data = resp.json()
            if data.get("errcode") != 0:
                raise Exception(f"企微token获取失败: {data}")
            return data["access_token"]

    async def sync_organization(self, db: AsyncSession) -> dict:
        from app.models.department import Department
        from app.models.user import User
        from app.utils.auth import get_password_hash
        from sqlalchemy import select

        token = await self.get_access_token()
        stats = {"departments_added": 0, "users_added": 0, "users_updated": 0}

        import httpx
        async with httpx.AsyncClient() as client:
            # 1. 获取部门
            dept_resp = await client.get(
                "https://qyapi.weixin.qq.com/cgi-bin/department/list",
                params={"access_token": token}
            )
            dept_data = dept_resp.json()

            dept_id_map = {0: None}
            for dd in dept_data.get("department", []):
                ext_id = dd.get("id")
                parent_ext_id = dd.get("parentid", 0)
                result = await db.execute(
                    select(Department).where(Department.name == dd.get("name"))
                )
                dept = result.scalar_one_or_none()
                if not dept:
                    dept = Department(
                        name=dd.get("name", "未知"),
                        parent_id=dept_id_map.get(parent_ext_id),
                        sort=dd.get("order", 0),
                        is_active=True,
                    )
                    db.add(dept)
                    await db.flush()
                    stats["departments_added"] += 1
                dept_id_map[ext_id] = dept.id

            # 2. 获取员工
            async def fetch_dept_users(dept_id: int):
                user_resp = await client.get(
                    "https://qyapi.weixin.qq.com/cgi-bin/user/list",
                    params={"access_token": token, "department_id": dept_id, "fetch_child": 1}
                )
                return user_resp.json()

            for ext_id, local_id in dept_id_map.items():
                if ext_id == 0: continue
                user_data = await fetch_dept_users(ext_id)
                for u in user_data.get("userlist", []):
                    username = u.get("userid") or u.get("mobile", "")
                    if not username:
                        continue
                    result = await db.execute(
                        select(User).where(User.username == username[:50])
                    )
                    user = result.scalar_one_or_none()
                    if user:
                        user.real_name = u.get("name", user.real_name)
                        user.email = u.get("email") or user.email
                        user.phone = u.get("mobile") or user.phone
                        user.department_id = local_id
                        stats["users_updated"] += 1
                    else:
                        user = User(
                            username=str(username)[:50],
                            real_name=u.get("name", ""),
                            email=u.get("email"),
                            phone=u.get("mobile"),
                            password_hash=get_password_hash("123456"),
                            role="student",
                            department_id=local_id,
                            is_active=True,
                        )
                        db.add(user)
                        stats["users_added"] += 1

        return {"platform": "wecom", **stats}

    async def send_message(self, user_ids: list[str], content: str) -> dict:
        token = await self.get_access_token()
        agent_id = self.config.get("agent_id")
        if not agent_id:
            raise ValueError("企微配置缺失: agent_id")

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://qyapi.weixin.qq.com/cgi-bin/message/send",
                params={"access_token": token},
                json={
                    "touser": "|".join(user_ids),
                    "msgtype": "markdown",
                    "agentid": int(agent_id),
                    "markdown": {"content": content}
                }
            )
            return resp.json()


# ========================================================================
# 工厂函数
# ========================================================================

PLATFORM_MAP = {
    "dingtalk": DingTalkConnector,
    "feishu": FeishuConnector,
    "wecom": WeComConnector,
}


def get_connector(platform: str, config_json: str | dict) -> Optional[PlatformConnector]:
    """获取平台连接器实例"""
    cls = PLATFORM_MAP.get(platform)
    if not cls:
        return None
    if isinstance(config_json, str):
        config = json.loads(config_json) if config_json else {}
    else:
        config = config_json or {}
    return cls(config)
