#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

# 允许直接执行: uv run python scripts/init_admin_users.py
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.password import hash_password
from app.core.rbac_permissions import (
    DEFAULT_PERMISSION_DEFINITIONS,
    SUPER_ADMIN_ROLE_CODE,
    SUPER_ADMIN_ROLE_NAME,
)
from app.db.session import AsyncSessionLocal, close_db
from app.models.admin import Admin
from app.models.rbac import RbacAdminRole, RbacPermission, RbacRole, RbacRolePermission

SEED_USERS = [
    {"username": "admin", "nickname": "admin", "code": "A001"},
    {"username": "super", "nickname": "super", "code": "A002"},
    {"username": "test", "nickname": "test", "code": "A003"},
]


async def init_users(password: str) -> None:
    created = 0
    updated = 0
    rbac_permission_created = 0
    rbac_permission_updated = 0
    rbac_role_created = 0
    rbac_admin_role_created = 0
    rbac_role_permission_created = 0
    rbac_init_success = True
    admin_columns = set(Admin.__table__.columns.keys())
    users_by_username: dict[str, Admin] = {}

    async with AsyncSessionLocal() as session:
        for item in SEED_USERS:
            username = item["username"]
            stmt = select(Admin).where(Admin.username == username).order_by(Admin.id.asc())
            records = (await session.execute(stmt)).scalars().all()

            if not records:
                create_data = {
                    "username": username,
                    "nickname": item["nickname"],
                    "code": item["code"],
                    "password": hash_password(password),
                    "is_tourist": 1,
                    "login_type": "single",
                    "creator": "seed",
                    "modifier": "seed",
                    "remark": "init script",
                }
                if "status" in admin_columns:
                    create_data["status"] = 1
                if "is_deleted" in admin_columns:
                    create_data["is_deleted"] = 0

                session.add(
                    Admin(**create_data)
                )
                created += 1
                continue

            user = records[0]
            user.password = hash_password(password)
            user.login_type = user.login_type or "single"
            user.modifier = "seed"
            user.remark = "init script reset password"
            if "status" in admin_columns:
                user.status = 1
            if "is_deleted" in admin_columns:
                user.is_deleted = 0
            user.touch()
            updated += 1

            if len(records) > 1:
                print(f"[WARN] 用户名 {username} 存在 {len(records)} 条记录，仅更新了最早一条(id={user.id})")

        await session.flush()

        for item in SEED_USERS:
            username = item["username"]
            user_stmt = select(Admin).where(Admin.username == username).order_by(Admin.id.asc())
            user = (await session.execute(user_stmt)).scalars().first()
            if user:
                users_by_username[username] = user

        await session.commit()

        try:
            permission_codes = [item["code"] for item in DEFAULT_PERMISSION_DEFINITIONS]
            permission_stmt = select(RbacPermission).where(RbacPermission.code.in_(permission_codes))
            permission_records = (await session.execute(permission_stmt)).scalars().all()
            permission_map = {item.code: item for item in permission_records}

            for item in DEFAULT_PERMISSION_DEFINITIONS:
                code = item["code"]
                permission = permission_map.get(code)
                if not permission:
                    session.add(RbacPermission(**item, status=1, is_deleted=0))
                    rbac_permission_created += 1
                    continue

                permission.name = item["name"]
                permission.group_key = item["group_key"]
                permission.api_path = item["api_path"]
                permission.api_method = item["api_method"]
                permission.sort = item["sort"]
                permission.remark = item["remark"]
                permission.status = 1
                permission.is_deleted = 0
                permission.touch()
                rbac_permission_updated += 1

            await session.flush()

            role_stmt = select(RbacRole).where(RbacRole.code == SUPER_ADMIN_ROLE_CODE).order_by(RbacRole.id.asc())
            super_admin_role = (await session.execute(role_stmt)).scalars().first()
            if not super_admin_role:
                super_admin_role = RbacRole(
                    name=SUPER_ADMIN_ROLE_NAME,
                    code=SUPER_ADMIN_ROLE_CODE,
                    is_system=1,
                    status=1,
                    is_deleted=0,
                    remark="init script",
                )
                session.add(super_admin_role)
                await session.flush()
                rbac_role_created += 1
            else:
                super_admin_role.name = SUPER_ADMIN_ROLE_NAME
                super_admin_role.is_system = 1
                super_admin_role.status = 1
                super_admin_role.is_deleted = 0
                super_admin_role.remark = "init script"
                super_admin_role.touch()

            refresh_permission_stmt = select(RbacPermission).where(
                RbacPermission.code.in_(permission_codes),
                RbacPermission.is_deleted == 0,
            )
            all_permissions = (await session.execute(refresh_permission_stmt)).scalars().all()
            permission_ids = {item.id for item in all_permissions}

            role_permission_stmt = select(RbacRolePermission).where(RbacRolePermission.role_id == super_admin_role.id)
            role_permissions = (await session.execute(role_permission_stmt)).scalars().all()
            role_permission_map = {item.permission_id: item for item in role_permissions}

            for permission_id in permission_ids:
                rel = role_permission_map.get(permission_id)
                if rel:
                    rel.status = 1
                    rel.is_deleted = 0
                    rel.touch()
                    continue
                session.add(
                    RbacRolePermission(
                        role_id=super_admin_role.id,
                        permission_id=permission_id,
                        status=1,
                        is_deleted=0,
                    )
                )
                rbac_role_permission_created += 1

            for permission_id, rel in role_permission_map.items():
                if permission_id in permission_ids:
                    continue
                rel.status = 0
                rel.is_deleted = 1
                rel.touch()

            for username in ("admin", "super", "test"):
                user = users_by_username.get(username)
                if not user:
                    continue
                admin_role_stmt = select(RbacAdminRole).where(
                    RbacAdminRole.admin_id == user.id,
                    RbacAdminRole.role_id == super_admin_role.id,
                )
                admin_role = (await session.execute(admin_role_stmt)).scalars().first()
                if admin_role:
                    admin_role.status = 1
                    admin_role.is_deleted = 0
                    admin_role.touch()
                    continue
                session.add(
                    RbacAdminRole(
                        admin_id=user.id,
                        role_id=super_admin_role.id,
                        status=1,
                        is_deleted=0,
                    )
                )
                rbac_admin_role_created += 1

            await session.commit()
        except Exception as exc:
            rbac_init_success = False
            await session.rollback()
            print(f"[WARN] RBAC 初始化失败，已跳过: {exc}")

    print(f"[OK] 初始化完成: created={created}, updated={updated}, total={len(SEED_USERS)}")
    if rbac_init_success:
        print(
            "[OK] RBAC 初始化完成: "
            f"permissions(created={rbac_permission_created}, updated={rbac_permission_updated}), "
            f"roles(created={rbac_role_created}), "
            f"role_permissions(created={rbac_role_permission_created}), "
            f"admin_roles(created={rbac_admin_role_created})"
        )
    else:
        print("[WARN] RBAC 初始化未完成，请先执行数据库迁移后重试")
    print(f"[OK] 用户: {', '.join(x['username'] for x in SEED_USERS)}; 密码: {password}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="初始化后台用户(admin/super/test)")
    parser.add_argument("--password", default="123456", help="初始化密码，默认 123456")
    return parser.parse_args()


async def _main() -> None:
    args = parse_args()
    try:
        await init_users(args.password)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(_main())
