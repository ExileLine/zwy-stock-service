"""add inbound_record_id to stock_outbound_record

Revision ID: 7f8f9c2d4b11
Revises: 08800922a0c2
Create Date: 2026-04-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f8f9c2d4b11"
down_revision: Union[str, Sequence[str], None] = "08800922a0c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "stock_outbound_record",
        sa.Column("inbound_record_id", sa.Integer(), nullable=True, comment="关联入库记录ID"),
    )
    op.create_index(
        "ix_stock_outbound_record_inbound_record_id",
        "stock_outbound_record",
        ["inbound_record_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stock_outbound_record_inbound_record_id", table_name="stock_outbound_record")
    op.drop_column("stock_outbound_record", "inbound_record_id")
