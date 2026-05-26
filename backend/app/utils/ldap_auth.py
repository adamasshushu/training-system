"""
LDAP/AD 认证工具

认证流程（两步绑定）：
1. 用管理员账号搜索用户 DN
2. 用用户 DN + 密码尝试绑定 → 成功即认证通过

配置来源：企业平台配置表(enterprise_configs)中的 ldap 平台配置
"""

import json
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def ldap_authenticate(username: str, password: str, db: AsyncSession = None) -> Optional[dict]:
    """
    LDAP/AD 用户认证

    从 enterprise_configs 表中读取 ldap 平台配置。
    使用管理员账号搜索用户，然后用用户凭据验证。

    Returns:
        dict with username/real_name/email/phone 或 None（认证失败/未配置）
    """
    if not db:
        return None

    try:
        # 读取 LDAP 配置
        config = await _get_ldap_config(db)
        if not config:
            return None

        import ldap3

        server_url = config.get('server', '')
        port = int(config.get('port', 389))
        domain = config.get('domain', '')
        admin_user = config.get('username', 'Administrator')
        admin_password = config.get('password', '')
        base_dn = config.get('base_dn', '')

        # 自动推导 base_dn
        if not base_dn and domain:
            base_dn = ','.join(f'DC={p}' for p in domain.split('.'))
        if not base_dn:
            base_dn = 'DC=cyb-org,DC=cn'

        # 构建管理员 bind_dn
        if domain:
            admin_dn = f'CN={admin_user},CN=Users,{base_dn}'
        else:
            admin_dn = config.get('bind_dn', f'CN={admin_user},CN=Users,{base_dn}')

        # Step 1: 用管理员账号连接
        server = ldap3.Server(server_url, port=port, get_info=ldap3.ALL)
        admin_conn = ldap3.Connection(server, user=admin_dn, password=admin_password, auto_bind=True)

        # Step 2: 搜索用户 DN
        search_filter = f'(sAMAccountName={username})'
        admin_conn.search(
            search_base=base_dn,
            search_filter=search_filter,
            attributes=['distinguishedName', 'displayName', 'mail', 'mobile',
                       'department', 'employeeID', 'userAccountControl'],
            search_scope=ldap3.SUBTREE,
        )

        if len(admin_conn.entries) == 0:
            logger.info(f"LDAP 未找到用户: {username}")
            admin_conn.unbind()
            return None

        entry = admin_conn.entries[0]
        user_dn = str(entry.distinguishedName)

        # 检查账号是否禁用
        try:
            uac = int(entry.userAccountControl.value or 0)
            if uac & 2:  # ACCOUNTDISABLE
                logger.warning(f"LDAP 用户已禁用: {username}")
                admin_conn.unbind()
                return None
        except (AttributeError, ValueError, TypeError):
            pass

        admin_conn.unbind()

        # Step 3: 用用户凭据验证
        user_conn = ldap3.Connection(server, user=user_dn, password=password)
        if not user_conn.bind():
            logger.warning(f"LDAP 密码错误: {username}")
            return None

        user_conn.unbind()

        # Step 4: 返回用户信息
        real_name = str(entry.displayName) if entry.displayName else username
        email = str(entry.mail) if entry.mail else f'{username}@cyb-org.cn'
        phone = str(entry.mobile) if entry.mobile else None
        department = str(entry.department) if entry.department else None

        logger.info(f"LDAP 认证成功: {username} ({real_name})")
        return {
            "username": username,
            "real_name": real_name,
            "email": email,
            "phone": phone,
            "department": department,
        }

    except ImportError:
        logger.warning("ldap3 未安装，LDAP 认证不可用")
        return None
    except Exception as e:
        logger.error(f"LDAP 认证异常: {e}")
        return None


async def _get_ldap_config(db: AsyncSession) -> Optional[dict]:
    """从 enterprise_configs 表读取 LDAP 配置"""
    try:
        from app.models.enterprise import EnterpriseConfig
        result = await db.execute(
            select(EnterpriseConfig).where(
                EnterpriseConfig.platform == 'ldap',
                EnterpriseConfig.is_enabled == True,
            )
        )
        config = result.scalar_one_or_none()
        if not config or not config.config_json:
            return None
        return json.loads(config.config_json)
    except Exception as e:
        logger.warning(f"读取 LDAP 配置失败: {e}")
        return None
