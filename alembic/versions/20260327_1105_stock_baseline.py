"""stock baseline

Revision ID: 20260327_1105
Revises:
Create Date: 2026-03-27 11:05:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260327_1105"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stock_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="ID"),
        sa.Column("product_name", sa.String(length=255), nullable=False, comment="产品名称"),
        sa.Column("product_brand", sa.String(length=255), nullable=True, comment="产品品牌"),
        sa.Column("product_spec", sa.Text(), nullable=True, comment="产品规格"),
        sa.Column("pn_code", sa.String(length=255), nullable=True, comment="PN码"),
        sa.Column("material_code", sa.String(length=128), nullable=True, comment="物料编码"),
        sa.Column("major_category", sa.String(length=64), nullable=True, comment="大类编码"),
        sa.Column("category_serial_no", sa.String(length=64), nullable=True, comment="分类序号"),
        sa.Column("category_suffix_code", sa.String(length=64), nullable=True, comment="小码"),
        sa.Column("applicable_device_model", sa.String(length=255), nullable=True, comment="适用设备型号"),
        sa.Column("device_type", sa.String(length=64), nullable=True, comment="设备类型"),
        sa.Column("source_sheet", sa.String(length=64), nullable=False, server_default="产品分类", comment="来源工作表"),
        sa.Column("source_row_no", sa.Integer(), nullable=True, comment="来源Excel行号"),
        sa.Column("remark", sa.String(length=255), nullable=True, comment="备注"),
        sa.Column("create_time", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("update_time", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("create_timestamp", sa.BigInteger(), nullable=False, comment="创建时间戳"),
        sa.Column("update_timestamp", sa.BigInteger(), nullable=False, comment="更新时间戳"),
        sa.Column("is_deleted", sa.BigInteger(), nullable=True, server_default="0", comment="逻辑删除标识"),
        sa.Column("status", sa.BigInteger(), nullable=True, server_default="1", comment="状态(通用字段)"),
        sa.PrimaryKeyConstraint("id"),
        comment="库存分类表",
    )
    op.create_index("ix_stock_category_major_category", "stock_category", ["major_category"], unique=False)
    op.create_index("ix_stock_category_material_code", "stock_category", ["material_code"], unique=False)
    op.create_index("ix_stock_category_pn_code", "stock_category", ["pn_code"], unique=False)

    op.create_table(
        "stock_in_out_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="ID"),
        sa.Column("row_no", sa.Integer(), nullable=True, comment="原始序号"),
        sa.Column("category_id", sa.Integer(), nullable=True, comment="分类ID(冗余关联,不加外键约束)"),
        sa.Column("is_outbound", sa.Integer(), nullable=False, server_default="0", comment="是否已出库:0-在库,1-已出库"),
        sa.Column("category_name", sa.String(length=64), nullable=True, comment="类别"),
        sa.Column("product_type", sa.String(length=64), nullable=True, comment="产品类型"),
        sa.Column("product_name", sa.String(length=255), nullable=False, comment="产品名称"),
        sa.Column("product_brand", sa.String(length=255), nullable=True, comment="产品品牌"),
        sa.Column("product_spec", sa.String(length=255), nullable=True, comment="产品规格"),
        sa.Column("product_description", sa.Text(), nullable=True, comment="产品描述"),
        sa.Column("pn_code", sa.String(length=255), nullable=True, comment="PN码"),
        sa.Column("material_code", sa.String(length=128), nullable=True, comment="物料编码"),
        sa.Column("serial_number", sa.String(length=255), nullable=True, comment="序列号"),
        sa.Column("target_device_type", sa.String(length=64), nullable=True, comment="用于设备类型"),
        sa.Column("target_device_brand", sa.String(length=64), nullable=True, comment="用于设备品牌"),
        sa.Column("target_device_model", sa.String(length=255), nullable=True, comment="用于设备型号"),
        sa.Column("major_category", sa.String(length=64), nullable=True, comment="大类"),
        sa.Column("usage_scene", sa.String(length=255), nullable=True, comment="用途/设备挂载说明"),
        sa.Column("document_no", sa.String(length=128), nullable=True, comment="单号"),
        sa.Column("inbound_qty", sa.Integer(), nullable=True, comment="入库数量"),
        sa.Column("inbound_date", sa.Date(), nullable=True, comment="入库日期"),
        sa.Column("inbound_room", sa.String(length=128), nullable=True, comment="入库机房"),
        sa.Column("storage_location", sa.String(length=255), nullable=True, comment="存放位置"),
        sa.Column("stock_qty", sa.Integer(), nullable=True, comment="库存数量"),
        sa.Column("outbound_qty", sa.Integer(), nullable=True, comment="领用数量"),
        sa.Column("outbound_date", sa.Date(), nullable=True, comment="领用日期"),
        sa.Column("actual_device_type", sa.String(length=64), nullable=True, comment="领用后设备类型"),
        sa.Column("actual_device_brand", sa.String(length=64), nullable=True, comment="领用后设备品牌"),
        sa.Column("actual_device_model", sa.String(length=255), nullable=True, comment="领用后设备型号"),
        sa.Column("device_position", sa.String(length=255), nullable=True, comment="设备位置"),
        sa.Column("original_owner_org", sa.String(length=255), nullable=True, comment="原归属用户单位"),
        sa.Column("target_room", sa.String(length=128), nullable=True, comment="用于机房"),
        sa.Column("remark", sa.String(length=255), nullable=True, comment="备注"),
        sa.Column("expansion_remark", sa.String(length=255), nullable=True, comment="扩容备注"),
        sa.Column("source_sheet", sa.String(length=64), nullable=False, server_default="出入库明细表", comment="来源工作表"),
        sa.Column("source_row_no", sa.Integer(), nullable=True, comment="来源Excel行号"),
        sa.Column("create_time", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("update_time", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("create_timestamp", sa.BigInteger(), nullable=False, comment="创建时间戳"),
        sa.Column("update_timestamp", sa.BigInteger(), nullable=False, comment="更新时间戳"),
        sa.Column("is_deleted", sa.BigInteger(), nullable=True, server_default="0", comment="逻辑删除标识"),
        sa.Column("status", sa.BigInteger(), nullable=True, server_default="1", comment="状态(通用字段)"),
        sa.PrimaryKeyConstraint("id"),
        comment="库存出入库记录表",
    )
    op.create_index("ix_stock_in_out_record_category_id", "stock_in_out_record", ["category_id"], unique=False)
    op.create_index("ix_stock_in_out_record_document_no", "stock_in_out_record", ["document_no"], unique=False)
    op.create_index("ix_stock_in_out_record_inbound_date", "stock_in_out_record", ["inbound_date"], unique=False)
    op.create_index("ix_stock_in_out_record_is_outbound", "stock_in_out_record", ["is_outbound"], unique=False)
    op.create_index("ix_stock_in_out_record_material_code", "stock_in_out_record", ["material_code"], unique=False)
    op.create_index("ix_stock_in_out_record_outbound_date", "stock_in_out_record", ["outbound_date"], unique=False)
    op.create_index("ix_stock_in_out_record_pn_code", "stock_in_out_record", ["pn_code"], unique=False)
    op.create_index("ix_stock_in_out_record_serial_number", "stock_in_out_record", ["serial_number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stock_in_out_record_serial_number", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_pn_code", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_outbound_date", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_material_code", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_is_outbound", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_inbound_date", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_document_no", table_name="stock_in_out_record")
    op.drop_index("ix_stock_in_out_record_category_id", table_name="stock_in_out_record")
    op.drop_table("stock_in_out_record")

    op.drop_index("ix_stock_category_pn_code", table_name="stock_category")
    op.drop_index("ix_stock_category_material_code", table_name="stock_category")
    op.drop_index("ix_stock_category_major_category", table_name="stock_category")
    op.drop_table("stock_category")
