# -*- coding: utf-8 -*-
# @Time    : 2026/3/10
# @Author  : yangyuexiong
# @File    : rbac.py

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import CommonPydanticCreate, CommonPydanticUpdate
from app.schemas.pagination import CommonPage


class RbacPermissionCreateReqData(CommonPydanticCreate):
    name: str = Field(description="权限名称", min_length=1, max_length=128)
    code: str = Field(description="权限编码", min_length=1, max_length=128)
    group_key: Optional[str] = Field(default=None, description="分组标识", max_length=64)
    api_path: Optional[str] = Field(default=None, description="接口路径", max_length=255)
    api_method: Optional[str] = Field(default=None, description="请求方法", max_length=16)
    sort: int = Field(default=0, description="排序值")


class RbacPermissionUpdateReqData(CommonPydanticUpdate):
    id: int = Field(description="权限ID")
    name: Optional[str] = Field(default=None, description="权限名称", min_length=1, max_length=128)
    group_key: Optional[str] = Field(default=None, description="分组标识", max_length=64)
    api_path: Optional[str] = Field(default=None, description="接口路径", max_length=255)
    api_method: Optional[str] = Field(default=None, description="请求方法", max_length=16)
    sort: Optional[int] = Field(default=None, description="排序值")
    status: Optional[int] = Field(default=None, description="状态")


class RbacPermissionPageReqData(CommonPage):
    is_deleted: int = 0
    status: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    group_key: Optional[str] = None


class RbacRoleCreateReqData(CommonPydanticCreate):
    name: str = Field(description="角色名称", min_length=1, max_length=64)
    code: str = Field(description="角色编码", min_length=1, max_length=64)
    is_system: int = Field(default=0, description="是否系统内置:0否1是")


class RbacRoleUpdateReqData(CommonPydanticUpdate):
    id: int = Field(description="角色ID")
    name: Optional[str] = Field(default=None, description="角色名称", min_length=1, max_length=64)
    status: Optional[int] = Field(default=None, description="状态")
    is_system: Optional[int] = Field(default=None, description="是否系统内置:0否1是")


class RbacRolePageReqData(CommonPage):
    is_deleted: int = 0
    status: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    is_system: Optional[int] = None


class RbacRoleBindPermissionsReqData(BaseModel):
    role_id: int = Field(description="角色ID")
    permission_ids: list[int] = Field(default_factory=list, description="权限ID列表")


class RbacAdminBindRolesReqData(BaseModel):
    admin_id: int = Field(description="用户ID")
    role_ids: list[int] = Field(default_factory=list, description="角色ID列表")

