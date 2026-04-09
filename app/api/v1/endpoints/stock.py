# -*- coding: utf-8 -*-

from fastapi import APIRouter, Body, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_exception import CustomException
from app.core.response import api_response
from app.db.session import get_db_session
from app.models.stock import StockInboundRecord, StockOutboundRecord
from app.schemas.pagination import page_size, query_result
from app.schemas.stock import (
    StockInboundCreate,
    StockInboundDelete,
    StockInboundPageQuery,
    StockInboundUpdate,
    StockOutboundCreateFromInbound,
    StockOutboundPageQuery,
)
from app.utils.time_tools import TimeTools

router = APIRouter(prefix="/stock", tags=["stock"])


async def _ensure_inbound_record_not_referenced(
        inbound_record_id: int,
        db_session: AsyncSession,
) -> None:
    stmt = select(StockOutboundRecord.id).where(
        StockOutboundRecord.inbound_record_id == inbound_record_id,
        StockOutboundRecord.is_deleted == 0,
    )
    outbound_record_id = (await db_session.execute(stmt)).scalar_one_or_none()
    if outbound_record_id is not None:
        raise CustomException(detail="该入库记录已存在出库记录，不允许操作", custom_code=10005)


@router.post("/page", summary="库存列表(分页模糊搜索)")
async def list_stock_records(
        request_data: StockInboundPageQuery = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    filters = [StockInboundRecord.is_deleted == 0]

    like_mapping = {
        "major_category": request_data.major_category,
        "product_type": request_data.product_type,
        "product_name": request_data.product_name,
        "product_brand": request_data.product_brand,
        "product_spec": request_data.product_spec,
        "pn_code": request_data.pn_code,
        "material_code": request_data.material_code,
        "serial_number": request_data.serial_number,
        "applicable_device_type": request_data.applicable_device_type,
        "applicable_device_model": request_data.applicable_device_model,
        "purchase_order_no": request_data.purchase_order_no,
        "supplier": request_data.supplier,
        "warranty_period": request_data.warranty_period,
        "inbound_room": request_data.inbound_room,
        "storage_location": request_data.storage_location,
    }
    for field, value in like_mapping.items():
        if value:
            filters.append(getattr(StockInboundRecord, field).ilike(f"%{value}%"))

    if request_data.keyword:
        keyword = f"%{request_data.keyword}%"
        filters.append(
            or_(
                StockInboundRecord.major_category.ilike(keyword),
                StockInboundRecord.product_type.ilike(keyword),
                StockInboundRecord.product_name.ilike(keyword),
                StockInboundRecord.product_brand.ilike(keyword),
                StockInboundRecord.product_spec.ilike(keyword),
                StockInboundRecord.pn_code.ilike(keyword),
                StockInboundRecord.material_code.ilike(keyword),
                StockInboundRecord.serial_number.ilike(keyword),
                StockInboundRecord.applicable_device_type.ilike(keyword),
                StockInboundRecord.applicable_device_model.ilike(keyword),
                StockInboundRecord.purchase_order_no.ilike(keyword),
                StockInboundRecord.supplier.ilike(keyword),
                StockInboundRecord.warranty_period.ilike(keyword),
                StockInboundRecord.inbound_room.ilike(keyword),
                StockInboundRecord.storage_location.ilike(keyword),
                StockInboundRecord.product_description.ilike(keyword),
                StockInboundRecord.remark.ilike(keyword),
            )
        )

    count_stmt = select(func.count()).select_from(StockInboundRecord).where(*filters)
    total = (await db_session.execute(count_stmt)).scalar_one()

    offset, limit = page_size(request_data.page, request_data.size)
    stmt = (
        select(StockInboundRecord)
        .where(*filters)
        .order_by(StockInboundRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    records = (await db_session.execute(stmt)).scalars().all()

    result = []
    for record in records:
        item = record.to_dict()
        if item.get("create_time"):
            item["create_time"] = TimeTools.convert_to_standard_format(item["create_time"])
        if item.get("update_time"):
            item["update_time"] = TimeTools.convert_to_standard_format(item["update_time"])
        result.append(item)

    return api_response(
        data=query_result(records=result, now_page=request_data.page, total=total),
        is_pop=False,
    )


@router.post("/create", summary="新增库存")
async def create_stock_record(
        request_data: StockInboundCreate = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    record = StockInboundRecord(**request_data.dict())
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return api_response(code=201, data=record.to_dict())


@router.post("/update", summary="编辑库存")
async def update_stock_record(
        request_data: StockInboundUpdate = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    await _ensure_inbound_record_not_referenced(request_data.id, db_session)

    stmt = select(StockInboundRecord).where(
        StockInboundRecord.id == request_data.id,
        StockInboundRecord.is_deleted == 0,
    )
    record = (await db_session.execute(stmt)).scalar_one_or_none()
    if record is None:
        raise CustomException(detail="未找到数据", custom_code=10002)

    update_data = request_data.dict(exclude={"id"})
    for key, value in update_data.items():
        setattr(record, key, value)
    record.touch()
    await db_session.commit()
    await db_session.refresh(record)
    return api_response(code=203, data=record.to_dict())


@router.post("/delete", summary="删除库存")
async def delete_stock_record(
        request_data: StockInboundDelete = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    await _ensure_inbound_record_not_referenced(request_data.id, db_session)

    stmt = select(StockInboundRecord).where(
        StockInboundRecord.id == request_data.id,
        StockInboundRecord.is_deleted == 0,
    )
    record = (await db_session.execute(stmt)).scalar_one_or_none()
    if record is None:
        raise CustomException(detail="未找到数据", custom_code=10002)

    record.is_deleted = 1
    record.touch()
    await db_session.commit()
    return api_response(code=204)


@router.post("/outbound/page", summary="出库记录列表(分页模糊搜索)")
async def list_stock_outbound_records(
        request_data: StockOutboundPageQuery = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    filters = [StockOutboundRecord.is_deleted == 0]

    like_mapping = {
        "product_serial_number": request_data.product_serial_number,
        "product_name": request_data.product_name,
        "product_brand": request_data.product_brand,
        "product_spec": request_data.product_spec,
        "pn_code": request_data.pn_code,
        "material_code": request_data.material_code,
        "usage_purpose": request_data.usage_purpose,
        "target_device_serial_number": request_data.target_device_serial_number,
        "target_room": request_data.target_room,
        "target_device_location": request_data.target_device_location,
        "owner_org": request_data.owner_org,
    }
    for field, value in like_mapping.items():
        if value:
            filters.append(getattr(StockOutboundRecord, field).ilike(f"%{value}%"))

    if request_data.keyword:
        keyword = f"%{request_data.keyword}%"
        filters.append(
            or_(
                StockOutboundRecord.product_serial_number.ilike(keyword),
                StockOutboundRecord.product_name.ilike(keyword),
                StockOutboundRecord.product_brand.ilike(keyword),
                StockOutboundRecord.product_spec.ilike(keyword),
                StockOutboundRecord.pn_code.ilike(keyword),
                StockOutboundRecord.material_code.ilike(keyword),
                StockOutboundRecord.usage_purpose.ilike(keyword),
                StockOutboundRecord.target_device_serial_number.ilike(keyword),
                StockOutboundRecord.target_room.ilike(keyword),
                StockOutboundRecord.target_device_location.ilike(keyword),
                StockOutboundRecord.owner_org.ilike(keyword),
                StockOutboundRecord.remark.ilike(keyword),
            )
        )

    count_stmt = select(func.count()).select_from(StockOutboundRecord).where(*filters)
    total = (await db_session.execute(count_stmt)).scalar_one()

    offset, limit = page_size(request_data.page, request_data.size)
    stmt = (
        select(StockOutboundRecord)
        .where(*filters)
        .order_by(StockOutboundRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    records = (await db_session.execute(stmt)).scalars().all()

    result = []
    for record in records:
        item = record.to_dict()
        if item.get("create_time"):
            item["create_time"] = TimeTools.convert_to_standard_format(item["create_time"])
        if item.get("update_time"):
            item["update_time"] = TimeTools.convert_to_standard_format(item["update_time"])
        result.append(item)

    return api_response(
        data=query_result(records=result, now_page=request_data.page, total=total),
        is_pop=False,
    )


@router.post("/outbound/create", summary="出库")
async def create_stock_outbound_record(
        request_data: StockOutboundCreateFromInbound = Body(...),
        db_session: AsyncSession = Depends(get_db_session),
):
    stmt = (
        select(StockInboundRecord)
        .where(
            StockInboundRecord.id == request_data.inbound_record_id,
            StockInboundRecord.is_deleted == 0,
        )
        .with_for_update()
    )
    inbound_record = (await db_session.execute(stmt)).scalar_one_or_none()
    if inbound_record is None:
        raise CustomException(detail="未找到入库数据", custom_code=10002)

    available_qty = inbound_record.inbound_qty or 0
    if available_qty < request_data.outbound_qty:
        raise CustomException(detail="出库数量不足", custom_code=10005)

    record = StockOutboundRecord(
        inbound_record_id=inbound_record.id,
        outbound_date=request_data.outbound_date,
        product_serial_number=inbound_record.serial_number,
        product_name=inbound_record.product_name,
        product_brand=inbound_record.product_brand,
        product_spec=inbound_record.product_spec,
        pn_code=inbound_record.pn_code,
        material_code=inbound_record.material_code,
        outbound_qty=request_data.outbound_qty,
        usage_purpose=request_data.usage_purpose,
        target_device_serial_number=request_data.target_device_serial_number,
        target_room=request_data.target_room,
        target_device_location=request_data.target_device_location,
        owner_org=request_data.owner_org,
        remark=request_data.remark,
    )
    db_session.add(record)
    inbound_record.inbound_qty = available_qty - request_data.outbound_qty
    inbound_record.touch()
    await db_session.commit()
    await db_session.refresh(record)
    return api_response(code=201, data=record.to_dict())
