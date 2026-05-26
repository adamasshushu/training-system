"""
AD 实时服务 — 对标 AdDomainPlatform AdService.cs

从 enterprise_configs 读取 ldap 配置，提供实时 AD 操作：
- OU 树浏览
- 用户搜索（关键词、OU 筛选）
- 用户详情
- 重置密码、启用/禁用、解锁

不缓存 AD 数据到本地 DB（区别于 enterprise_connector 的同步逻辑）。
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LdapService:
    """AD 实时操作服务"""

    def __init__(self, config: dict):
        self.server_url = config.get("server", "")
        self.port = int(config.get("port", 389))
        self.domain = config.get("domain", "")
        self.admin_user = config.get("username", "Administrator")
        self.admin_password = config.get("password", "")
        self.base_dn = config.get("base_dn", "")
        self.use_ssl = config.get("use_ssl", False)

        # 自动推导 base_dn
        if not self.base_dn and self.domain:
            self.base_dn = ",".join(f"DC={p}" for p in self.domain.split("."))
        if not self.base_dn:
            self.base_dn = "DC=cyb-org,DC=cn"

        # 管理员 bind DN
        if self.domain:
            self.bind_dn = config.get("bind_dn") or f"CN={self.admin_user},CN=Users,{self.base_dn}"
        else:
            self.bind_dn = config.get("bind_dn", f"CN={self.admin_user},CN=Users,{self.base_dn}")

    # ═══════════════ 连接管理 ═══════════════

    def _connect(self):
        """建立 LDAP 连接"""
        import ldap3
        server = ldap3.Server(
            self.server_url, port=self.port, use_ssl=self.use_ssl, get_info=ldap3.ALL
        )
        conn = ldap3.Connection(server, user=self.bind_dn, password=self.admin_password, auto_bind=True)
        return conn

    @staticmethod
    def _attr(entry, name: str) -> str:
        """安全提取属性"""
        try:
            val = getattr(entry, name, None)
            return str(val) if val else ""
        except Exception:
            return ""

    @staticmethod
    def _is_disabled(entry) -> bool:
        """检查用户是否禁用 (ACCOUNTDISABLE flag)"""
        try:
            uac = entry.userAccountControl
            return bool(uac and (int(uac.value or 0) & 2))
        except Exception:
            return False

    @staticmethod
    def _is_locked(entry) -> bool:
        """检查用户是否锁定"""
        try:
            lt = entry.lockoutTime
            return bool(lt and int(lt.value or 0) > 0)
        except Exception:
            return False

    # ═══════════════ 测试连接 ═══════════════

    async def test_connection(self) -> tuple:
        """测试 AD 连接"""
        try:
            conn = self._connect()
            conn.unbind()
            return True, "连接成功"
        except Exception as e:
            return False, str(e)

    # ═══════════════ OU 树 ═══════════════

    async def get_ou_tree(self) -> list:
        """
        获取实时 AD OU 树 — 对标 AdService.GetOuTreeWithUsersAsync
        
        Returns:
            [{名称, 识别名, 描述, 用户数, 子部门: [...]}]
        """
        import ldap3
        try:
            conn = self._connect()
        except Exception as e:
            return [{"error": f"连接失败: {e}"}]

        try:
            # 查所有 OU
            conn.search(
                self.base_dn,
                "(objectClass=organizationalUnit)",
                attributes=["ou", "distinguishedName", "description", "whenCreated"],
                search_scope=ldap3.SUBTREE,
            )

            ous = []
            for entry in conn.entries:
                ou_name = self._attr(entry, "ou")
                dn = self._attr(entry, "distinguishedName")
                ous.append({
                    "名称": ou_name,
                    "识别名": dn,
                    "描述": self._attr(entry, "description"),
                    "创建时间": self._attr(entry, "whenCreated"),
                    "深度": dn.lower().count(",ou="),  # OU depth for sorting
                })

            # 按 DN 深度排序（浅层先）
            ous.sort(key=lambda x: x["深度"])

            # 统计每个 OU 下的用户数
            for ou in ous:
                conn.search(
                    ou["识别名"],
                    "(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))",
                    attributes=["sAMAccountName"],
                    search_scope=ldap3.LEVEL,
                )
                ou["用户数"] = len(conn.entries) if conn.entries else 0
                del ou["深度"]  # 内部字段

            # 构建树形结构
            tree = self._build_ou_tree(ous)
        finally:
            conn.unbind()

        return tree

    def _build_ou_tree(self, ous: list) -> list:
        """递归构建 OU 树 — 对标 AdService 的父子关系分配"""
        # 找顶级节点（DN 不以任何其他 OU 的 DN 结尾，除非是自己）
        top_level = []
        child_map = {}  # parent_dn_lower → [children]

        for ou in ous:
            dn_lower = ou["识别名"].lower()
            # 找父 OU：去掉第一个 OU=xxx 部分
            parts = dn_lower.split(",", 1)
            parent_dn = parts[1] if len(parts) > 1 else ""

            # 检查 parent_dn 是否在 ous 中
            found_parent = any(p["识别名"].lower() == parent_dn for p in ous)
            if not found_parent:
                top_level.append(ou)
            else:
                child_map.setdefault(parent_dn, []).append(ou)

        # 递归填充子部门
        def fill_children(node):
            key = node["识别名"].lower()
            children = child_map.get(key, [])
            node["子部门"] = children
            for child in children:
                fill_children(child)

        for node in top_level:
            fill_children(node)

        return top_level

    # ═══════════════ 用户搜索 ═══════════════

    async def search_users(self, keyword: str = "", ou_dn: str = "") -> list:
        """
        实时搜索 AD 用户 — 对标 AdService.SearchUsersAsync
        
        Args:
            keyword: 搜索关键词 (sAMAccountName, displayName, mail)
            ou_dn: 限定 OU (留空搜索整个域)
        """
        import ldap3
        try:
            conn = self._connect()
        except Exception:
            return []

        search_base = ou_dn or self.base_dn
        scope = ldap3.LEVEL if ou_dn else ldap3.SUBTREE

        if keyword:
            escaped = keyword.replace("(", "\\28").replace(")", "\\29")
            filter_str = (
                f"(&(objectClass=user)(objectCategory=person)"
                f"(|(sAMAccountName=*{escaped}*)(displayName=*{escaped}*)(mail=*{escaped}*)(cn=*{escaped}*)))"
            )
        else:
            filter_str = "(&(objectClass=user)(objectCategory=person))"

        attrs = [
            "sAMAccountName", "displayName", "mail", "mobile",
            "department", "title", "employeeID", "distinguishedName",
            "userAccountControl", "lockoutTime", "whenCreated", "lastLogon",
            "givenName", "sn", "physicalDeliveryOfficeName",
            "telephoneNumber", "company", "manager",
        ]

        try:
            conn.search(search_base, filter_str, attributes=attrs, search_scope=scope)
            users = []
            for entry in conn.entries:
                sam = self._attr(entry, "sAMAccountName")
                if not sam or sam.endswith("$"):
                    continue
                users.append(self._map_user(entry))

            # 排序：先启用的，再按 displayName
            users.sort(key=lambda u: (not u["启用"], u["显示名"].lower()))
        finally:
            conn.unbind()

        return users

    def _map_user(self, entry) -> dict:
        """映射用户为基础信息 — 对标 AdUserInfo"""
        sam = self._attr(entry, "sAMAccountName")
        display = self._attr(entry, "displayName") or sam
        dn = self._attr(entry, "distinguishedName")
        disabled = self._is_disabled(entry)
        locked = self._is_locked(entry)

        # 从 DN 提取 OU 路径
        ou_path = ""
        if dn:
            parts = dn.split(",", 1)
            ou_path = parts[1] if len(parts) > 1 else ""

        return {
            "用户名": sam,
            "显示名": display,
            "邮箱": self._attr(entry, "mail"),
            "部门": self._attr(entry, "department"),
            "职务": self._attr(entry, "title"),
            "识别名": dn,
            "OU路径": ou_path,
            "启用": not disabled,
            "已锁定": locked,
            "创建时间": self._attr(entry, "whenCreated"),
        }

    # ═══════════════ 用户详情 ═══════════════

    async def get_user_detail(self, dn: str) -> Optional[dict]:
        """
        获取 AD 用户完整详情 — 对标 AdService.GetUserDetailAsync (7 个属性 Tab)
        """
        import ldap3
        try:
            conn = self._connect()
        except Exception:
            return None

        attrs = [
            # 常规
            "sAMAccountName", "userPrincipalName", "displayName",
            "givenName", "sn", "description",
            "physicalDeliveryOfficeName", "telephoneNumber",
            "mail", "wWWHomePage",
            # 地址
            "streetAddress", "l", "st", "postalCode", "c",
            # 电话
            "homePhone", "pager", "mobile", "ipPhone", "info",
            # 组织
            "title", "department", "company", "manager", "directReports",
            # 账户
            "distinguishedName", "userAccountControl", "accountExpires",
            "lastLogon", "whenCreated", "lockoutTime",
            # 配置文件
            "profilePath", "scriptPath", "homeDirectory", "homeDrive",
            # 组成员
            "memberOf",
        ]

        try:
            conn.search(dn, "(objectClass=*)", attributes=attrs, search_scope=ldap3.BASE)
            if not conn.entries:
                return None

            entry = conn.entries[0]
            uac_str = self._attr(entry, "userAccountControl")
            uac = int(uac_str) if uac_str.isdigit() else 512

            detail = {
                # 常规
                "用户名": self._attr(entry, "sAMAccountName"),
                "UPN": self._attr(entry, "userPrincipalName"),
                "显示名": self._attr(entry, "displayName"),
                "姓": self._attr(entry, "sn"),
                "名": self._attr(entry, "givenName"),
                "描述": self._attr(entry, "description"),
                "办公室": self._attr(entry, "physicalDeliveryOfficeName"),
                "电话号码": self._attr(entry, "telephoneNumber"),
                "电子邮件": self._attr(entry, "mail"),
                "网页": self._attr(entry, "wWWHomePage"),
                # 地址
                "街道": self._attr(entry, "streetAddress"),
                "城市": self._attr(entry, "l"),
                "省": self._attr(entry, "st"),
                "邮编": self._attr(entry, "postalCode"),
                "国家": self._attr(entry, "c"),
                # 电话
                "家庭电话": self._attr(entry, "homePhone"),
                "寻呼机": self._attr(entry, "pager"),
                "手机": self._attr(entry, "mobile"),
                "IP电话": self._attr(entry, "ipPhone"),
                "备注": self._attr(entry, "info"),
                # 组织
                "职务": self._attr(entry, "title"),
                "部门": self._attr(entry, "department"),
                "公司": self._attr(entry, "company"),
                "经理DN": self._attr(entry, "manager"),
                # 账户
                "识别名": self._attr(entry, "distinguishedName"),
                "启用": not (uac & 2),
                "密码永不过期": bool(uac & 0x10000),
                "不能更改密码": bool(uac & 0x40),
                "密码已过期": bool(uac & 0x800000),
                "已锁定": self._is_locked(entry),
                "创建时间": self._attr(entry, "whenCreated"),
                "最后登录": self._attr(entry, "lastLogon"),
                # 配置文件
                "配置文件路径": self._attr(entry, "profilePath"),
                "登录脚本": self._attr(entry, "scriptPath"),
                "主文件夹": self._attr(entry, "homeDirectory"),
                "主驱动器": self._attr(entry, "homeDrive"),
                # 组
                "所属组": self._attr_multi(entry, "memberOf") if hasattr(entry, "memberOf") else [],
            }
        finally:
            conn.unbind()

        return detail

    @staticmethod
    def _attr_multi(entry, name: str) -> list:
        """提取多值属性"""
        try:
            val = getattr(entry, name, None)
            if val and hasattr(val, "values"):
                return [str(v) for v in val.values]
            return []
        except Exception:
            return []

    # ═══════════════ 用户操作 ═══════════════

    async def reset_password(self, dn: str, new_password: str) -> tuple:
        """重置 AD 用户密码 — 对标 AdService.ResetPasswordAsync"""
        import ldap3
        try:
            conn = self._connect()

            # unicodePwd 需要 UTF-16LE 编码，用引号包裹
            raw = f'"{new_password}"'.encode("utf-16-le")
            conn.modify(dn, {"unicodePwd": [(ldap3.MODIFY_REPLACE, [raw])]})

            if conn.result["result"] == 0:
                msg = "密码重置成功"
                ok = True
            else:
                msg = f"密码重置失败: {conn.result.get('description', '未知错误')}"
                ok = False

            conn.unbind()
            return ok, msg
        except Exception as e:
            return False, str(e)

    async def set_user_status(self, dn: str, enable: bool) -> tuple:
        """启用/禁用 AD 用户 — 对标 AdService.SetUserStatusAsync"""
        import ldap3
        try:
            conn = self._connect()

            # 读取当前 uac
            conn.search(dn, "(objectClass=*)", attributes=["userAccountControl"], search_scope=ldap3.BASE)
            if not conn.entries:
                conn.unbind()
                return False, "用户不存在"

            uac_str = self._attr(conn.entries[0], "userAccountControl")
            uac = int(uac_str) if uac_str.isdigit() else 512

            if enable:
                new_uac = uac & ~0x0002  # 清除 ACCOUNTDISABLE
            else:
                new_uac = uac | 0x0002   # 设置 ACCOUNTDISABLE

            conn.modify(dn, {"userAccountControl": [(ldap3.MODIFY_REPLACE, [str(new_uac)])]})

            ok = conn.result["result"] == 0
            action = "已启用" if enable else "已禁用"
            msg = action if ok else f"操作失败: {conn.result.get('description', '')}"

            conn.unbind()
            return ok, msg
        except Exception as e:
            return False, str(e)

    async def unlock_user(self, dn: str) -> tuple:
        """解锁 AD 账户 — 对标 AdService.UnlockUserAsync"""
        import ldap3
        try:
            conn = self._connect()
            conn.modify(dn, {"lockoutTime": [(ldap3.MODIFY_REPLACE, ["0"])]})

            ok = conn.result["result"] == 0
            msg = "账户已解锁" if ok else f"解锁失败: {conn.result.get('description', '')}"

            conn.unbind()
            return ok, msg
        except Exception as e:
            return False, str(e)


# ═══════════════ 工厂函数 ═══════════════

async def get_ldap_service(db) -> Optional[LdapService]:
    """从企业平台配置表读取 LDAP 配置并创建服务实例"""
    try:
        from sqlalchemy import select
        from app.models.enterprise import EnterpriseConfig

        result = await db.execute(
            select(EnterpriseConfig).where(
                EnterpriseConfig.platform == "ldap",
                EnterpriseConfig.is_enabled == True,
            )
        )
        config_row = result.scalar_one_or_none()
        if not config_row or not config_row.config_json:
            return None

        config = json.loads(config_row.config_json)
        return LdapService(config)
    except Exception as e:
        logger.warning(f"创建 LdapService 失败: {e}")
        return None
