# -*- coding: utf-8 -*-
# @Time    : 2026/3/10
# @Author  : yangyuexiong
# @File    : rbac.py

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CustomBaseModel


class RbacRole(CustomBaseModel):
    """角色表"""

    __table_name__ = "rbac_roles"
    __table_args__ = (
        UniqueConstraint("name", name="uq_rbac_role_name"),
        UniqueConstraint("code", name="uq_rbac_role_code"),
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色编码")
    is_system: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="是否系统内置角色:0否1是")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")


class RbacPermission(CustomBaseModel):
    """权限点表"""

    __table_name__ = "rbac_permissions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_rbac_permission_code"),
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="权限名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, comment="权限编码")
    group_key: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="分组标识")
    api_path: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="接口路径")
    api_method: Mapped[str | None] = mapped_column(String(16), nullable=True, comment="请求方法")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="排序值")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")


class RbacAdminRole(CustomBaseModel):
    """用户角色关联表(无外键约束)"""

    __table_name__ = "rbac_admin_roles"
    __table_args__ = (
        UniqueConstraint("admin_id", "role_id", name="uq_rbac_admin_role"),
    )

    admin_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="用户ID")
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="角色ID")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")


class RbacRolePermission(CustomBaseModel):
    """角色权限关联表(无外键约束)"""

    __table_name__ = "rbac_role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_rbac_role_permission"),
    )

    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="角色ID")
    permission_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="权限ID")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")
