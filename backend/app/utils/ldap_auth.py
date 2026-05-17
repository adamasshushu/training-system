"""LDAP认证工具"""
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def ldap_authenticate(username: str, password: str) -> Optional[dict]:
    """
    LDAP用户认证

    配置方式（在.env或系统设置中）:
        LDAP_SERVER=ldap://ldap.company.com:389
        LDAP_BASE_DN=dc=company,dc=com
        LDAP_USER_FILTER=(sAMAccountName={username})  # AD
        LDAP_ATTR_NAME=displayName
        LDAP_ATTR_EMAIL=mail
        LDAP_ATTR_PHONE=telephoneNumber

    如果LDAP未配置，返回None（走本地密码认证）
    """
    ldap_server = getattr(settings, "LDAP_SERVER", None) or await _get_env_setting("LDAP_SERVER")
    if not ldap_server:
        return None  # LDAP未配置，走本地认证

    base_dn = getattr(settings, "LDAP_BASE_DN", None) or await _get_env_setting("LDAP_BASE_DN", "")
    user_filter = getattr(settings, "LDAP_USER_FILTER", None) or await _get_env_setting("LDAP_USER_FILTER", "(uid={username})")
    attr_name = getattr(settings, "LDAP_ATTR_NAME", None) or await _get_env_setting("LDAP_ATTR_NAME", "cn")
    attr_email = getattr(settings, "LDAP_ATTR_EMAIL", None) or await _get_env_setting("LDAP_ATTR_EMAIL", "mail")
    attr_phone = getattr(settings, "LDAP_ATTR_PHONE", None) or await _get_env_setting("LDAP_ATTR_PHONE", "telephoneNumber")

    try:
        import ldap3
        server = ldap3.Server(ldap_server, get_info=ldap3.ALL)
        conn = ldap3.Connection(server, user=f"cn={username},{base_dn}" if base_dn else username, password=password)

        if not conn.bind():
            logger.warning(f"LDAP认证失败: {username}")
            return None

        # 查找用户信息
        search_filter = user_filter.replace("{username}", username)
        conn.search(
            search_base=base_dn,
            search_filter=search_filter,
            attributes=[attr_name, attr_email, attr_phone],
        )

        if len(conn.entries) == 0:
            logger.warning(f"LDAP未找到用户: {username}")
            return None

        entry = conn.entries[0]
        return {
            "username": username,
            "real_name": str(getattr(entry, attr_name, username)),
            "email": str(getattr(entry, attr_email, "")),
            "phone": str(getattr(entry, attr_phone, "")),
        }

    except ImportError:
        logger.warning("ldap3 未安装，LDAP认证不可用")
        return None
    except Exception as e:
        logger.error(f"LDAP认证异常: {e}")
        return None


async def _get_env_setting(key: str, default: str = "") -> str:
    """从.env读取配置"""
    import os
    return os.environ.get(key, default)
