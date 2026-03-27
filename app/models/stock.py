# -*- coding: utf-8 -*-
# @Time    : 2026-03-27
# @Author  : Codex
# @File    : stock.py

from datetime import date

from sqlalchemy import Date, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CustomBaseModel


class StockCategory(CustomBaseModel):
    __table_name__ = "stock_category"

    product_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    product_brand: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品品牌")
    product_spec: Mapped[str | None] = mapped_column(Text, nullable=True, comment="产品规格")
    pn_code: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="PN码")
    material_code: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="物料编码")
    major_category: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="大类编码")
    category_serial_no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="分类序号")
    category_suffix_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="小码")
    applicable_device_model: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="适用设备型号")
    device_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="设备类型")
    source_sheet: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="产品分类",
        server_default=text("'产品分类'"),
        comment="来源工作表",
    )
    source_row_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="来源Excel行号")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")

    __table_args__ = (
        Index("ix_stock_category_material_code", "material_code"),
        Index("ix_stock_category_pn_code", "pn_code"),
        Index("ix_stock_category_major_category", "major_category"),
        {"comment": "库存分类表"},
    )


class StockInOutRecord(CustomBaseModel):
    __table_name__ = "stock_in_out_record"

    row_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="原始序号")
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="分类ID(冗余关联,不加外键约束)")
    is_outbound: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="是否已出库:0-在库,1-已出库",
    )
    category_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="类别")
    product_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="产品类型")
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    product_brand: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品品牌")
    product_spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品规格")
    product_description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="产品描述")
    pn_code: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="PN码")
    material_code: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="物料编码")
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="序列号")
    target_device_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="用于设备类型")
    target_device_brand: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="用于设备品牌")
    target_device_model: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用于设备型号")
    major_category: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="大类")
    usage_scene: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用途/设备挂载说明")
    document_no: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="单号")
    inbound_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="入库数量")
    inbound_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="入库日期")
    inbound_room: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="入库机房")
    storage_location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="存放位置")
    stock_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="库存数量")
    outbound_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="领用数量")
    outbound_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="领用日期")
    actual_device_type: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="领用后设备类型")
    actual_device_brand: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="领用后设备品牌")
    actual_device_model: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="领用后设备型号")
    device_position: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="设备位置")
    original_owner_org: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="原归属用户单位")
    target_room: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="用于机房")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="备注")
    expansion_remark: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="扩容备注")
    source_sheet: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="出入库明细表",
        server_default=text("'出入库明细表'"),
        comment="来源工作表",
    )
    source_row_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="来源Excel行号")

    __table_args__ = (
        Index("ix_stock_in_out_record_category_id", "category_id"),
        Index("ix_stock_in_out_record_is_outbound", "is_outbound"),
        Index("ix_stock_in_out_record_document_no", "document_no"),
        Index("ix_stock_in_out_record_material_code", "material_code"),
        Index("ix_stock_in_out_record_pn_code", "pn_code"),
        Index("ix_stock_in_out_record_serial_number", "serial_number"),
        Index("ix_stock_in_out_record_inbound_date", "inbound_date"),
        Index("ix_stock_in_out_record_outbound_date", "outbound_date"),
        {"comment": "库存出入库记录表"},
    )
