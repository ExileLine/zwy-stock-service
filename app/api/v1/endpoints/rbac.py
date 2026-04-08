# -*- coding: utf-8 -*-
# @Time    : 2026/3/10
# @Author  : yangyuexiong
# @File    : rbac.py

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception_handlers import CustomException
from app.core.response import api_response
from app.core.security import (
    check_admin_existence,
    query_admin_permission_codes,
    query_admin_role_codes,
    require_permissions,
)
from app.db.session import get_db_session
from app.models.admin import Admin
from app.models.rbac import RbacAdminRole, RbacPermission, RbacRole, RbacRolePermission
from app.schemas.pagination import query_result
from app.schemas.rbac import (
    RbacAdminBindRolesReqData,
    RbacPermissionCreateReqData,
    RbacPermissionPageReqData,
    RbacPermissionUpdateReqData,
    RbacRoleBindPermissionsReqData,
    RbacRoleCreateReqData,
    RbacRolePageReqData,
    RbacRoleUpdateReqData,
)

router = APIRouter(prefix="/rbac", tags=["权限角色"])


def _normalize_http_method(api_method: str | None) -> str | None:
    if api_method is None:
        return None
    value = api_method.strip().upper()
    return value or None


def _pick_model_columns(model, data: dict) -> dict:
    columns = set(model.__table__.columns.keys())
    return {k: v for k, v in data.items() if k in columns}


async def _get_role_or_raise(db: AsyncSession, role_id: int) -> RbacRole:
    role = (await db.execute(select(RbacRole).where(RbacRole.id == role_id, RbacRole.is_deleted == 0))).scalars().first()
    if not role:
        raise CustomException(detail=f"角色 {role_id} 不存在", custom_code=10002)
    return role


async def _get_permission_or_raise(db: AsyncSession, permission_id: int) -> RbacPermission:
    permission = (
        await db.execute(select(RbacPermission).where(RbacPermission.id == permission_id, RbacPermission.is_deleted == 0))
    ).scalars().first()
    if not permission:
        raise CustomException(detail=f"权限 {permission_id} 不存在", custom_code=10002)
    return permission


@router.post("/permission", summary="新增权限")
async def create_permission(
        request_data: RbacPermissionCreateReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    dup_stmt = select(RbacPermission).where(
        RbacPermission.code == request_data.code,
    )
    dup = (await db.execute(dup_stmt)).scalars().first()
    if dup:
        raise CustomException(detail=f"权限编码 {request_data.code} 已存在", custom_code=10003)

    save_data = _pick_model_columns(RbacPermission, request_data.dict())
    save_data["api_method"] = _normalize_http_method(request_data.api_method)
    db.add(RbacPermission(**save_data))
    await db.commit()
    return api_response(http_code=status.HTTP_201_CREATED, code=201)


@router.put("/permission", summary="编辑权限")
async def update_permission(
        request_data: RbacPermissionUpdateReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    permission = await _get_permission_or_raise(db, request_data.id)

    if request_data.name is not None and not request_data.name.strip():
        raise CustomException(detail="权限名称不能为空", custom_code=10001)

    update_data = _pick_model_columns(RbacPermission, request_data.dict())
    update_data.pop("id", None)
    if "api_method" in update_data:
        update_data["api_method"] = _normalize_http_method(update_data["api_method"])
    for k, v in update_data.items():
        setattr(permission, k, v)
    permission.touch()
    await db.commit()
    return api_response(code=203, message="编辑成功")


@router.delete("/permission/{permission_id}", summary="删除权限")
async def delete_permission(
        permission_id: int,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    permission = await _get_permission_or_raise(db, permission_id)
    permission.is_deleted = 1
    permission.status = 0
    permission.touch()

    relation_stmt = select(RbacRolePermission).where(
        RbacRolePermission.permission_id == permission_id,
        RbacRolePermission.is_deleted == 0,
    )
    relations = (await db.execute(relation_stmt)).scalars().all()
    for item in relations:
        item.is_deleted = 1
        item.status = 0
        item.touch()

    await db.commit()
    return api_response(code=204, message="删除成功")


@router.get("/permission/{permission_id}", summary="权限详情")
async def permission_detail(
        permission_id: int,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    permission = await _get_permission_or_raise(db, permission_id)
    return api_response(data=jsonable_encoder(permission.to_dict()))


@router.post("/permission/page", summary="权限分页")
async def permission_page(
        request_data: RbacPermissionPageReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    filters = [RbacPermission.is_deleted == request_data.is_deleted]
    if request_data.status is not None:
        filters.append(RbacPermission.status == request_data.status)
    if request_data.name:
        filters.append(RbacPermission.name.ilike(f"%{request_data.name}%"))
    if request_data.code:
        filters.append(RbacPermission.code.ilike(f"%{request_data.code}%"))
    if request_data.group_key:
        filters.append(RbacPermission.group_key == request_data.group_key)

    total_stmt = select(func.count()).select_from(RbacPermission).where(*filters)
    total = (await db.execute(total_stmt)).scalar_one()

    offset = (request_data.page - 1) * request_data.size
    stmt = (
        select(RbacPermission)
        .where(*filters)
        .order_by(RbacPermission.sort.asc(), RbacPermission.id.asc())
        .offset(offset)
        .limit(request_data.size)
    )
    rows = (await db.execute(stmt)).scalars().all()
    records = [row.to_dict() for row in rows]
    return api_response(data=query_result(records=records, now_page=request_data.page, total=total))


@router.post("/role", summary="新增角色")
async def create_role(
        request_data: RbacRoleCreateReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    dup_stmt = select(RbacRole).where(
        or_(RbacRole.name == request_data.name, RbacRole.code == request_data.code),
    )
    dup = (await db.execute(dup_stmt)).scalars().all()
    for item in dup:
        if item.name == request_data.name:
            raise CustomException(detail=f"角色名称 {request_data.name} 已存在", custom_code=10003)
        if item.code == request_data.code:
            raise CustomException(detail=f"角色编码 {request_data.code} 已存在", custom_code=10003)

    db.add(RbacRole(**_pick_model_columns(RbacRole, request_data.dict())))
    await db.commit()
    return api_response(http_code=status.HTTP_201_CREATED, code=201)


@router.put("/role", summary="编辑角色")
async def update_role(
        request_data: RbacRoleUpdateReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    role = await _get_role_or_raise(db, request_data.id)
    if request_data.name is not None:
        check_name = request_data.name.strip()
        if not check_name:
            raise CustomException(detail="角色名称不能为空", custom_code=10001)
        dup_stmt = select(RbacRole).where(
            RbacRole.id != request_data.id,
            RbacRole.name == check_name,
        )
        dup_role = (await db.execute(dup_stmt)).scalars().first()
        if dup_role:
            raise CustomException(detail=f"角色名称 {check_name} 已存在", custom_code=10003)

    update_data = _pick_model_columns(RbacRole, request_data.dict())
    update_data.pop("id", None)
    for k, v in update_data.items():
        setattr(role, k, v)
    role.touch()
    await db.commit()
    return api_response(code=203, message="编辑成功")


@router.delete("/role/{role_id}", summary="删除角色")
async def delete_role(
        role_id: int,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    role = await _get_role_or_raise(db, role_id)
    if role.is_system == 1:
        raise CustomException(detail="系统内置角色不允许删除", custom_code=10005)

    role.is_deleted = 1
    role.status = 0
    role.touch()

    role_permission_stmt = select(RbacRolePermission).where(
        RbacRolePermission.role_id == role_id,
        RbacRolePermission.is_deleted == 0,
    )
    role_permissions = (await db.execute(role_permission_stmt)).scalars().all()
    for item in role_permissions:
        item.is_deleted = 1
        item.status = 0
        item.touch()

    admin_role_stmt = select(RbacAdminRole).where(
        RbacAdminRole.role_id == role_id,
        RbacAdminRole.is_deleted == 0,
    )
    admin_roles = (await db.execute(admin_role_stmt)).scalars().all()
    for item in admin_roles:
        item.is_deleted = 1
        item.status = 0
        item.touch()

    await db.commit()
    return api_response(code=204, message="删除成功")


@router.get("/role/{role_id}", summary="角色详情")
async def role_detail(
        role_id: int,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    role = await _get_role_or_raise(db, role_id)
    rel_stmt = select(RbacRolePermission.permission_id).where(
        RbacRolePermission.role_id == role_id,
        RbacRolePermission.is_deleted == 0,
        RbacRolePermission.status == 1,
    )
    permission_ids = (await db.execute(rel_stmt)).scalars().all()
    role_data = role.to_dict()
    role_data["permission_ids"] = permission_ids
    return api_response(data=jsonable_encoder(role_data))


@router.post("/role/page", summary="角色分页")
async def role_page(
        request_data: RbacRolePageReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    filters = [RbacRole.is_deleted == request_data.is_deleted]
    if request_data.status is not None:
        filters.append(RbacRole.status == request_data.status)
    if request_data.name:
        filters.append(RbacRole.name.ilike(f"%{request_data.name}%"))
    if request_data.code:
        filters.append(RbacRole.code.ilike(f"%{request_data.code}%"))
    if request_data.is_system is not None:
        filters.append(RbacRole.is_system == request_data.is_system)

    total_stmt = select(func.count()).select_from(RbacRole).where(*filters)
    total = (await db.execute(total_stmt)).scalar_one()

    offset = (request_data.page - 1) * request_data.size
    stmt = (
        select(RbacRole)
        .where(*filters)
        .order_by(RbacRole.update_time.desc(), RbacRole.id.desc())
        .offset(offset)
        .limit(request_data.size)
    )
    rows = (await db.execute(stmt)).scalars().all()
    records = [row.to_dict() for row in rows]
    return api_response(data=query_result(records=records, now_page=request_data.page, total=total))


@router.post("/role/bind_permissions", summary="角色绑定权限")
async def bind_role_permissions(
        request_data: RbacRoleBindPermissionsReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    role = await _get_role_or_raise(db, request_data.role_id)

    target_permission_ids = {pid for pid in request_data.permission_ids if pid > 0}
    if target_permission_ids:
        permissions_stmt = select(RbacPermission.id).where(
            RbacPermission.id.in_(target_permission_ids),
            RbacPermission.is_deleted == 0,
        )
        valid_permission_ids = set((await db.execute(permissions_stmt)).scalars().all())
        invalid_ids = sorted(target_permission_ids - valid_permission_ids)
        if invalid_ids:
            raise CustomException(detail=f"权限不存在: {invalid_ids}", custom_code=10002)

    relation_stmt = select(RbacRolePermission).where(RbacRolePermission.role_id == role.id)
    relations = (await db.execute(relation_stmt)).scalars().all()
    relation_map = {item.permission_id: item for item in relations}

    for permission_id, relation in relation_map.items():
        if permission_id in target_permission_ids:
            relation.is_deleted = 0
            relation.status = 1
        else:
            relation.is_deleted = 1
            relation.status = 0
        relation.touch()

    new_permission_ids = target_permission_ids - set(relation_map.keys())
    for permission_id in new_permission_ids:
        db.add(
            RbacRolePermission(
                role_id=role.id,
                permission_id=permission_id,
                status=1,
                is_deleted=0,
            )
        )

    await db.commit()
    return api_response(
        message="操作成功",
        data={
            "role_id": role.id,
            "permission_ids": sorted(target_permission_ids),
        },
    )


@router.post("/admin/bind_roles", summary="用户绑定角色")
async def bind_admin_roles(
        request_data: RbacAdminBindRolesReqData,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    target_admin = (await db.execute(select(Admin).where(Admin.id == request_data.admin_id, Admin.is_deleted == 0))).scalars().first()
    if not target_admin:
        raise CustomException(detail=f"用户 {request_data.admin_id} 不存在", custom_code=10002)

    target_role_ids = {rid for rid in request_data.role_ids if rid > 0}
    if target_role_ids:
        roles_stmt = select(RbacRole.id).where(RbacRole.id.in_(target_role_ids), RbacRole.is_deleted == 0)
        valid_role_ids = set((await db.execute(roles_stmt)).scalars().all())
        invalid_ids = sorted(target_role_ids - valid_role_ids)
        if invalid_ids:
            raise CustomException(detail=f"角色不存在: {invalid_ids}", custom_code=10002)

    relation_stmt = select(RbacAdminRole).where(RbacAdminRole.admin_id == target_admin.id)
    relations = (await db.execute(relation_stmt)).scalars().all()
    relation_map = {item.role_id: item for item in relations}

    for role_id, relation in relation_map.items():
        if role_id in target_role_ids:
            relation.is_deleted = 0
            relation.status = 1
        else:
            relation.is_deleted = 1
            relation.status = 0
        relation.touch()

    new_role_ids = target_role_ids - set(relation_map.keys())
    for role_id in new_role_ids:
        db.add(
            RbacAdminRole(
                admin_id=target_admin.id,
                role_id=role_id,
                status=1,
                is_deleted=0,
            )
        )

    await db.commit()
    return api_response(
        message="操作成功",
        data={
            "admin_id": target_admin.id,
            "role_ids": sorted(target_role_ids),
        },
    )


@router.get("/admin/{admin_id}/grant", summary="用户授权信息")
async def admin_grant_detail(
        admin_id: int,
        admin: Admin = Depends(require_permissions("rbac.manage")),
        db: AsyncSession = Depends(get_db_session),
):
    target_admin = (await db.execute(select(Admin).where(Admin.id == admin_id, Admin.is_deleted == 0))).scalars().first()
    if not target_admin:
        raise CustomException(detail=f"用户 {admin_id} 不存在", custom_code=10002)

    role_codes = sorted(await query_admin_role_codes(admin_id, db))
    permission_codes = sorted(await query_admin_permission_codes(admin_id, db))
    return api_response(
        data={
            "admin_id": admin_id,
            "username": target_admin.username,
            "role_codes": role_codes,
            "permission_codes": permission_codes,
        }
    )


@router.get("/me/permissions", summary="我的权限")
async def my_permissions(
        admin: Admin = Depends(check_admin_existence),
        db: AsyncSession = Depends(get_db_session),
):
    role_codes = sorted(await query_admin_role_codes(admin.id, db))
    permission_codes = sorted(await query_admin_permission_codes(admin.id, db))
    return api_response(
        data={
            "admin_id": admin.id,
            "username": admin.username,
            "role_codes": role_codes,
            "permission_codes": permission_codes,
        }
    )
