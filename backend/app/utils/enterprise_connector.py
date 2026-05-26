"""
企业平台连接器：钉钉/飞书/企微/LDAP

支持的平台：
- dingtalk: 钉钉
- feishu: 飞书
- wecom: 企业微信
- ldap: LDAP/AD 域控

每个连接器实现：
- test_connection() → (bool, str)
- sync_organization(db) → dict
- send_message(user_ids, content) → dict (LDAP 不支持)
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════ LDAP / AD 连接器 ═══════════════

class LdapConnector:
    """LDAP/Active Directory 组织同步连接器"""

    def __init__(self, config_json: str | dict):
        if isinstance(config_json, str):
            self.config = json.loads(config_json)
        else:
            self.config = config_json

        self.server = self.config.get('server', '')
        self.port = int(self.config.get('port', 389))
        self.use_ssl = self.config.get('use_ssl', False)
        self.username = self.config.get('username', 'Administrator')
        self.password = self.config.get('password', '')
        self.base_dn = self.config.get('base_dn', '')
        self.user_filter = self.config.get('user_filter', '(objectClass=user)')
        self.ou_filter = self.config.get('ou_filter', '(objectClass=organizationalUnit)')

        # Auto-construct bind_dn from domain + username
        domain = self.config.get('domain', '')
        if domain:
            domain_dn = ','.join(f'DC={p}' for p in domain.split('.'))
            self.bind_dn = self.config.get('bind_dn') or f'CN={self.username},CN=Users,{domain_dn}'
            if not self.base_dn:
                self.base_dn = domain_dn
        else:
            self.bind_dn = self.config.get('bind_dn', f'CN={self.username},CN=Users,DC=cyb-org,DC=cn')

        # Fallback: if no domain and no base_dn, derive from bind_dn
        if not self.base_dn and self.bind_dn:
            import re
            dcs = re.findall(r'DC=([^,]+)', self.bind_dn, re.IGNORECASE)
            if dcs:
                self.base_dn = ','.join(f'DC={dc}' for dc in dcs)
        if not self.base_dn:
            self.base_dn = 'DC=cyb-org,DC=cn'

    def _connect(self):
        """建立 LDAP 连接"""
        import ldap3
        server = ldap3.Server(self.server, port=self.port, use_ssl=self.use_ssl,
                              get_info=ldap3.ALL)
        conn = ldap3.Connection(server, user=self.bind_dn,
                               password=self.password, auto_bind=True)
        return conn

    async def test_connection(self) -> tuple[bool, str]:
        """测试 LDAP 连接"""
        try:
            conn = self._connect()
            conn.unbind()
            return (True, f"连接成功 - {self.server}")
        except Exception as e:
            return (False, f"连接失败: {str(e)}")

    async def sync_organization(self, db) -> dict:
        """从 LDAP 同步组织架构到培训系统"""
        import ldap3
        from app.models.user import User
        from app.models.department import Department
        from sqlalchemy import select

        stats = {
            'ous_synced': 0,
            'users_added': 0,
            'users_updated': 0,
            'users_skipped': 0,
            'errors': [],
        }

        try:
            conn = self._connect()
        except Exception as e:
            return {'error': f'LDAP 连接失败: {e}'}

        try:
            # ── Step 1: Sync OUs as departments (preserve hierarchy) ──
            conn.search(self.base_dn, self.ou_filter,
                       attributes=['ou', 'distinguishedName'],
                       search_scope=ldap3.SUBTREE)

            # Sort by DN depth (shallow first) so parents exist before children
            entries_sorted = sorted(
                conn.entries,
                key=lambda e: str(e.distinguishedName).count(',')
            )

            ou_map = {}  # dn_lower → department_id
            for entry in entries_sorted:
                ou_name = str(entry.ou) if entry.ou else str(entry.distinguishedName).split(',')[0][3:]
                dn = str(entry.distinguishedName)

                # Find parent OU from DN
                parent_id = None
                dn_parts = dn.split(',')
                if len(dn_parts) > 1:
                    parent_dn = ','.join(dn_parts[1:]).lower()
                    # Look up parent in ou_map (only non-domain parts)
                    parent_key = parent_dn
                    parent_id = ou_map.get(parent_key)

                # Check if department exists by name+parent
                result = await db.execute(
                    select(Department).where(
                        Department.name == ou_name,
                        Department.parent_id == parent_id
                    )
                )
                dept = result.scalar_one_or_none()

                if not dept:
                    dept = Department(
                        name=ou_name,
                        parent_id=parent_id,
                        sort=0,
                        is_active=True
                    )
                    db.add(dept)
                    await db.flush()

                ou_map[dn.lower()] = dept.id
                stats['ous_synced'] += 1

            # ── Step 2: Sync users ──
            attrs = ['sAMAccountName', 'displayName', 'mail', 'mobile',
                    'department', 'employeeID', 'distinguishedName',
                    'userAccountControl']
            conn.search(self.base_dn, self.user_filter,
                       attributes=attrs, search_scope=ldap3.SUBTREE)

            for entry in conn.entries:
                try:
                    sam = str(entry.sAMAccountName) if entry.sAMAccountName else ''
                    if not sam or sam.endswith('$'):  # Skip computer accounts
                        stats['users_skipped'] += 1
                        continue

                    # Check if disabled
                    uac = int(entry.userAccountControl.value or 0)
                    if uac & 2:  # ACCOUNTDISABLE
                        stats['users_skipped'] += 1
                        continue

                    username = sam.lower()
                    realname = str(entry.displayName) if entry.displayName else username
                    email = str(entry.mail) if entry.mail else f'{username}@cyb-org.cn'
                    phone = str(entry.mobile) if entry.mobile else None
                    dept_name = str(entry.department) if entry.department else None
                    emp_id = str(entry.employeeID) if entry.employeeID else None
                    user_dn = str(entry.distinguishedName).lower() if entry.distinguishedName else ''

                    # Find department
                    department_id = None
                    if dept_name:
                        # Direct department name match
                        for dn_key, dept_id in ou_map.items():
                            if dept_name.lower() in dn_key:
                                department_id = dept_id
                                break
                    if not department_id:
                        # Parent OU from DN
                        parent_dn = ','.join(user_dn.split(',')[1:]) if user_dn else ''
                        department_id = ou_map.get(parent_dn)

                    # Check if user exists
                    result = await db.execute(
                        select(User).where(User.username == username)
                    )
                    user = result.scalar_one_or_none()

                    if user:
                        # Update
                        user.real_name = realname or user.real_name
                        user.email = email or user.email
                        user.phone = phone or user.phone
                        user.department_id = department_id or user.department_id
                        user.source = 'ldap'
                        stats['users_updated'] += 1
                    else:
                        # Create
                        user = User(
                            username=username,
                            real_name=realname,
                            email=email,
                            phone=phone,
                            department_id=department_id,
                            role='student',
                            password_hash='__ldap__',
                            source='ldap',
                            is_active=True,
                        )
                        db.add(user)
                        stats['users_added'] += 1

                except Exception as e:
                    stats['errors'].append(f"{getattr(entry, 'sAMAccountName', '?')}: {e}")
                    stats['users_skipped'] += 1

        finally:
            conn.unbind()

        return stats

    async def send_message(self, user_ids: list[str], content: str) -> dict:
        """LDAP 不支持消息推送"""
        return {'error': 'LDAP/AD 不支持消息推送功能'}


# ═══════════════ 钉钉连接器 (stub) ═══════════════

class DingtalkConnector:
    def __init__(self, config_json):
        self.config = json.loads(config_json) if isinstance(config_json, str) else config_json

    async def test_connection(self):
        return (False, '钉钉连接器未实现（需要 AppKey/AppSecret）')

    async def sync_organization(self, db):
        return {'error': '钉钉同步未实现'}

    async def send_message(self, user_ids, content):
        return {'error': '钉钉消息推送未实现'}


class FeishuConnector:
    def __init__(self, config_json):
        self.config = json.loads(config_json) if isinstance(config_json, str) else config_json

    async def test_connection(self):
        return (False, '飞书连接器未实现')

    async def sync_organization(self, db):
        return {'error': '飞书同步未实现'}

    async def send_message(self, user_ids, content):
        return {'error': '飞书消息推送未实现'}


class WecomConnector:
    def __init__(self, config_json):
        self.config = json.loads(config_json) if isinstance(config_json, str) else config_json

    async def test_connection(self):
        return (False, '企业微信连接器未实现')

    async def sync_organization(self, db):
        return {'error': '企微同步未实现'}

    async def send_message(self, user_ids, content):
        return {'error': '企微消息推送未实现'}


# ═══════════════ 连接器工厂 ═══════════════

def get_connector(platform: str, config_json: str | dict):
    """根据平台类型返回对应的连接器实例"""
    connectors = {
        'ldap': LdapConnector,
        'dingtalk': DingtalkConnector,
        'feishu': FeishuConnector,
        'wecom': WecomConnector,
    }
    cls = connectors.get(platform)
    return cls(config_json) if cls else None
