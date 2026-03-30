# -*- coding: utf-8 -*-
# @Time    : 2026-03-30
# @Author  : Codex
# @File    : stock.py

from datetime import date

from sqlalchemy import Date, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CustomBaseModel


class StockInboundRecord(CustomBaseModel):
    __table_name__ = "stock_inbound_record"

    inbound_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="入库日期")
    major_category: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="大类")
    product_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="产品类型")
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    product_brand: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品品牌")
    product_spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品规格")
    pn_code: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="PN码")
    material_code: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="物料编码")
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="序列号")
    applicable_device_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="适用设备类型")
    applicable_device_model: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="适用设备型号")
    purchase_order_no: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="采购单号")
    inbound_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="入库数量")
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="单位")
    inbound_room: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="入库机房")
    storage_location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="存放位置")
    product_description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="产品描述")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")

    __table_args__ = (
        Index("ix_stock_inbound_record_inbound_date", "inbound_date"),
        Index("ix_stock_inbound_record_major_category", "major_category"),
        Index("ix_stock_inbound_record_product_type", "product_type"),
        Index("ix_stock_inbound_record_product_name", "product_name"),
        Index("ix_stock_inbound_record_material_code", "material_code"),
        Index("ix_stock_inbound_record_pn_code", "pn_code"),
        Index("ix_stock_inbound_record_serial_number", "serial_number"),
        Index("ix_stock_inbound_record_purchase_order_no", "purchase_order_no"),
        {"comment": "库存入库明细表"},
    )


class StockOutboundRecord(CustomBaseModel):
    __table_name__ = "stock_outbound_record"

    outbound_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="领用日期")
    product_serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品序列号")
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    product_brand: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品品牌")
    product_spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品规格")
    pn_code: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="PN码")
    material_code: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="物料编码")
    outbound_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="领用数量")
    usage_purpose: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用途")
    target_device_serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用于设备序列号")
    target_room: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="用于机房")
    target_device_location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用于设备位置")
    owner_org: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="设备归属用户单位")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")

    __table_args__ = (
        Index("ix_stock_outbound_record_outbound_date", "outbound_date"),
        Index("ix_stock_outbound_record_product_serial_number", "product_serial_number"),
        Index("ix_stock_outbound_record_product_name", "product_name"),
        Index("ix_stock_outbound_record_material_code", "material_code"),
        Index("ix_stock_outbound_record_pn_code", "pn_code"),
        Index("ix_stock_outbound_record_target_device_serial_number", "target_device_serial_number"),
        {"comment": "库存出库明细表"},
    )
