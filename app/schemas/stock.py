# -*- coding: utf-8 -*-

from datetime import date

from pydantic import ConfigDict, Field

from app.schemas.common import CommonPydanticCreate, CommonPydanticUpdate
from app.schemas.pagination import CommonPage


class StockInboundPageQuery(CommonPage):
    model_config = ConfigDict(extra="ignore")

    keyword: str | None = Field(default=None, description="全局关键字")
    major_category: str | None = Field(default=None, description="大类")
    product_type: str | None = Field(default=None, description="产品类型")
    product_name: str | None = Field(default=None, description="产品名称")
    product_brand: str | None = Field(default=None, description="产品品牌")
    product_spec: str | None = Field(default=None, description="产品规格")
    pn_code: str | None = Field(default=None, description="PN码")
    material_code: str | None = Field(default=None, description="物料编码")
    serial_number: str | None = Field(default=None, description="序列号")
    applicable_device_type: str | None = Field(default=None, description="适用设备类型")
    applicable_device_model: str | None = Field(default=None, description="适用设备型号")
    purchase_order_no: str | None = Field(default=None, description="采购单号")
    supplier: str | None = Field(default=None, description="供应商")
    warranty_period: str | None = Field(default=None, description="维保期")
    inbound_room: str | None = Field(default=None, description="入库机房")
    storage_location: str | None = Field(default=None, description="存放位置")


class StockInboundMajorCategoryStatPageQuery(CommonPage):
    model_config = ConfigDict(extra="ignore")

    keyword: str | None = Field(default=None, description="全局关键字")
    major_category: str | None = Field(default=None, description="大类")


class StockInboundByMajorCategoryPageQuery(CommonPage):
    model_config = ConfigDict(extra="ignore")

    major_category: str = Field(..., description="大类")
    keyword: str | None = Field(default=None, description="全局关键字")


class StockInboundCreate(CommonPydanticCreate):
    inbound_date: date | None = Field(default=None, description="入库日期")
    major_category: str | None = Field(default=None, description="大类")
    product_type: str | None = Field(default=None, description="产品类型")
    product_name: str = Field(..., description="产品名称")
    product_brand: str | None = Field(default=None, description="产品品牌")
    product_spec: str | None = Field(default=None, description="产品规格")
    pn_code: str | None = Field(default=None, description="PN码")
    material_code: str | None = Field(default=None, description="物料编码")
    serial_number: str | None = Field(default=None, description="序列号")
    applicable_device_type: str | None = Field(default=None, description="适用设备类型")
    applicable_device_model: str | None = Field(default=None, description="适用设备型号")
    purchase_order_no: str | None = Field(default=None, description="采购单号")
    supplier: str | None = Field(default=None, description="供应商")
    warranty_period: str | None = Field(default=None, description="维保期")
    inbound_qty: int | None = Field(default=None, description="入库数量")
    unit: str | None = Field(default=None, description="单位")
    inbound_room: str | None = Field(default=None, description="入库机房")
    storage_location: str | None = Field(default=None, description="存放位置")
    product_description: str | None = Field(default=None, description="产品描述")


class StockOutboundCreateFromInbound(CommonPydanticCreate):
    inbound_record_id: int = Field(..., description="入库记录ID")
    outbound_date: date | None = Field(default=None, description="领用日期")
    outbound_qty: int = Field(..., ge=1, description="领用数量")
    usage_purpose: str | None = Field(default=None, description="用途")
    target_device_serial_number: str | None = Field(default=None, description="用于设备序列号")
    target_room: str | None = Field(default=None, description="用于机房")
    target_device_location: str | None = Field(default=None, description="用于设备位置")
    owner_org: str | None = Field(default=None, description="设备归属用户单位")


class StockInboundUpdate(CommonPydanticUpdate):
    inbound_date: date | None = Field(default=None, description="入库日期")
    major_category: str | None = Field(default=None, description="大类")
    product_type: str | None = Field(default=None, description="产品类型")
    product_name: str | None = Field(default=None, description="产品名称")
    product_brand: str | None = Field(default=None, description="产品品牌")
    product_spec: str | None = Field(default=None, description="产品规格")
    pn_code: str | None = Field(default=None, description="PN码")
    material_code: str | None = Field(default=None, description="物料编码")
    serial_number: str | None = Field(default=None, description="序列号")
    applicable_device_type: str | None = Field(default=None, description="适用设备类型")
    applicable_device_model: str | None = Field(default=None, description="适用设备型号")
    purchase_order_no: str | None = Field(default=None, description="采购单号")
    supplier: str | None = Field(default=None, description="供应商")
    warranty_period: str | None = Field(default=None, description="维保期")
    inbound_qty: int | None = Field(default=None, description="入库数量")
    unit: str | None = Field(default=None, description="单位")
    inbound_room: str | None = Field(default=None, description="入库机房")
    storage_location: str | None = Field(default=None, description="存放位置")
    product_description: str | None = Field(default=None, description="产品描述")


class StockInboundDelete(CommonPydanticUpdate):
    id: int = Field(..., description="需要删除的数据ID")


class StockOutboundPageQuery(CommonPage):
    model_config = ConfigDict(extra="ignore")

    keyword: str | None = Field(default=None, description="全局关键字")
    product_serial_number: str | None = Field(default=None, description="产品序列号")
    product_name: str | None = Field(default=None, description="产品名称")
    product_brand: str | None = Field(default=None, description="产品品牌")
    product_spec: str | None = Field(default=None, description="产品规格")
    pn_code: str | None = Field(default=None, description="PN码")
    material_code: str | None = Field(default=None, description="物料编码")
    usage_purpose: str | None = Field(default=None, description="用途")
    target_device_serial_number: str | None = Field(default=None, description="用于设备序列号")
    target_room: str | None = Field(default=None, description="用于机房")
    target_device_location: str | None = Field(default=None, description="用于设备位置")
    owner_org: str | None = Field(default=None, description="设备归属用户单位")


class StockOutboundCreate(CommonPydanticCreate):
    outbound_date: date | None = Field(default=None, description="领用日期")
    product_serial_number: str | None = Field(default=None, description="产品序列号")
    product_name: str = Field(..., description="产品名称")
    product_brand: str | None = Field(default=None, description="产品品牌")
    product_spec: str | None = Field(default=None, description="产品规格")
    pn_code: str | None = Field(default=None, description="PN码")
    material_code: str | None = Field(default=None, description="物料编码")
    outbound_qty: int | None = Field(default=None, description="领用数量")
    usage_purpose: str | None = Field(default=None, description="用途")
    target_device_serial_number: str | None = Field(default=None, description="用于设备序列号")
    target_room: str | None = Field(default=None, description="用于机房")
    target_device_location: str | None = Field(default=None, description="用于设备位置")
    owner_org: str | None = Field(default=None, description="设备归属用户单位")
