# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 20:15
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : auth_api.py
# @Software: PyCharm

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import api_response
from app.core.security import get_token_header, query_admin_permission_codes, query_admin_role_codes
from app.db.session import get_db_session

router = APIRouter()


@router.get("", summary="用户详情")
async def user_info(admin=Depends(get_token_header), db: AsyncSession = Depends(get_db_session)):
    """用户详情"""

    admin.pop("password", None)
    admin_id = admin.get("id")
    if admin_id is not None:
        try:
            admin_id = int(admin_id)
            admin["role_codes"] = sorted(await query_admin_role_codes(admin_id, db))
            admin["permission_codes"] = sorted(await query_admin_permission_codes(admin_id, db))
        except (TypeError, ValueError):
            pass
    return api_response(data=jsonable_encoder(admin))
