# -*- coding: utf-8 -*-
# @Time    : 2026-03-26 17:52:34
# @Author  : yangyuexiong
# @File    : __init__.py

# 新增模型后，请在这里导入，供 Alembic 自动发现
from app.models.admin import Admin
from app.models.aps_task import ApsTask
from app.models.stock import StockInboundRecord, StockOutboundRecord

__all__ = [
    "Admin",
    "ApsTask",
    "StockInboundRecord",
    "StockOutboundRecord",
]
