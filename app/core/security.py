# -*- coding: utf-8 -*-
# @Time    : 2026-03-26 17:52:34
# @Author  : yangyuexiong
# @File    : security.py

import json
import secrets
from collections.abc import Iterable

from fastapi import Depends, Header
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.redis_client as rp
from app.core.exception_handlers import CustomException
from app.db.redis_client import get_value, set_key_value
from app.db.session import get_db_session
from app.models.admin import Admin
from app.models.rbac import RbacAdminRole, RbacPermission, RbacRole, RbacRolePermission

RBAC_ROOT_ADMIN_IDS = {1}
RBAC_ROOT_ADMIN_USERNAMES = {"admin"}


class Token:
    """
    Token
    """

    def __init__(self):
        self.token = None
        self.timeout = 3600 * 24 * 30

    async def gen_token(self):
        """
        生成token
        :return:
        """

        token = secrets.token_urlsafe(32)
        self.token = token
        return token

    @staticmethod
    async def get_user_info(token: str):
        """
        通过token或用户信息
        :param token:
        :return:
        """

        query_user_info = await get_value(token)
        if not query_user_info:
            return False
        else:
            user_info = json.loads(query_user_info)
            return user_info

    async def single_login(self, key: str, user_info_json_str: str):
        """单点登录"""

        # 获取该用户所有有效的key和token并且删除
        old_key_list = await rp.redis_pool.keys(pattern=f"{key}*")
        old_token_list = [await get_value(old_key) for old_key in old_key_list]
        if old_key_list or old_token_list:
            logger.debug(f"single_login revoke tokens: keys={len(old_key_list)} tokens={len(old_token_list)}")
        if old_key_list:
            await rp.redis_pool.delete(*old_key_list)
        if old_token_list:
            await rp.redis_pool.delete(*old_token_list)

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息

    async def many_login(self, key: str, user_info_json_str: str):
        """多点登录"""

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息


async def get_token_header(token: str = Header()):
    """校验token"""

    query_user_info = await get_value(token)
    if not query_user_info:
        raise CustomException(detail="未授权", custom_code=401)
    else:
        user_info = json.loads(query_user_info)
        return user_info


async def check_admin_existence(
        user_info: dict = Depends(get_token_header),
        db: AsyncSession = Depends(get_db_session),
):
    """检查后台用户是否存在"""

    try:
        admin_id = int(user_info.get("id"))
    except (TypeError, ValueError):
        raise CustomException(detail="无效的用户身份", custom_code=401)
    stmt = select(Admin).where(Admin.id == admin_id, Admin.is_deleted == 0)
    admin = (await db.execute(stmt)).scalars().first()
    if not admin:
        raise CustomException(detail=f"后台用户 {admin_id} 不存在", custom_code=10002)
    if admin.status == 99:
        raise CustomException(detail=f"后台用户 {admin_id} 已禁用", custom_code=401)
    return admin


def is_root_admin(admin: Admin) -> bool:
    return admin.id in RBAC_ROOT_ADMIN_IDS or (admin.username or "") in RBAC_ROOT_ADMIN_USERNAMES


def _normalize_codes(codes: str | Iterable[str]) -> list[str]:
    if isinstance(codes, str):
        data = [codes]
    else:
        data = list(codes)
    return [str(item).strip() for item in data if str(item).strip()]


async def query_admin_role_codes(admin_id: int, db: AsyncSession) -> set[str]:
    stmt = (
        select(RbacRole.code)
        .join(RbacAdminRole, RbacAdminRole.role_id == RbacRole.id)
        .where(
            RbacAdminRole.admin_id == admin_id,
            RbacAdminRole.is_deleted == 0,
            RbacAdminRole.status == 1,
            RbacRole.is_deleted == 0,
            RbacRole.status == 1,
        )
        .distinct()
    )
    rows = (await db.execute(stmt)).scalars().all()
    return {code for code in rows if code}


async def query_admin_permission_codes(admin_id: int, db: AsyncSession) -> set[str]:
    stmt = (
        select(RbacPermission.code)
        .join(RbacRolePermission, RbacRolePermission.permission_id == RbacPermission.id)
        .join(RbacRole, RbacRole.id == RbacRolePermission.role_id)
        .join(RbacAdminRole, RbacAdminRole.role_id == RbacRole.id)
        .where(
            RbacAdminRole.admin_id == admin_id,
            RbacAdminRole.is_deleted == 0,
            RbacAdminRole.status == 1,
            RbacRolePermission.is_deleted == 0,
            RbacRolePermission.status == 1,
            RbacRole.is_deleted == 0,
            RbacRole.status == 1,
            RbacPermission.is_deleted == 0,
            RbacPermission.status == 1,
        )
        .distinct()
    )
    rows = (await db.execute(stmt)).scalars().all()
    return {code for code in rows if code}


def require_roles(role_codes: str | Iterable[str], *, require_all: bool = False):
    required_codes = _normalize_codes(role_codes)

    async def _role_dependency(
            admin: Admin = Depends(check_admin_existence),
            db: AsyncSession = Depends(get_db_session),
    ) -> Admin:
        if not required_codes or is_root_admin(admin):
            return admin

        owned_codes = await query_admin_role_codes(admin.id, db)
        if require_all:
            missing = [code for code in required_codes if code not in owned_codes]
            if missing:
                raise CustomException(detail=f"无权限，缺少角色: {', '.join(missing)}", custom_code=401)
        else:
            if not any(code in owned_codes for code in required_codes):
                raise CustomException(detail="无权限，缺少角色授权", custom_code=401)
        return admin

    return _role_dependency


def require_permissions(permission_codes: str | Iterable[str], *, require_all: bool = False):
    required_codes = _normalize_codes(permission_codes)

    async def _permission_dependency(
            admin: Admin = Depends(check_admin_existence),
            db: AsyncSession = Depends(get_db_session),
    ) -> Admin:
        if not required_codes or is_root_admin(admin):
            return admin

        owned_codes = await query_admin_permission_codes(admin.id, db)
        if require_all:
            missing = [code for code in required_codes if code not in owned_codes]
            if missing:
                raise CustomException(detail=f"无权限，缺少权限点: {', '.join(missing)}", custom_code=401)
        else:
            if not any(code in owned_codes for code in required_codes):
                raise CustomException(detail="无权限，缺少权限点授权", custom_code=401)
        return admin

    return _permission_dependency
