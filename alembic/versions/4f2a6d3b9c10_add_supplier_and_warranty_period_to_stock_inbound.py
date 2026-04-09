"""add supplier and warranty_period to stock_inbound_record

Revision ID: 4f2a6d3b9c10
Revises: b55cce9cc203
Create Date: 2026-04-09 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4f2a6d3b9c10"
down_revision: Union[str, Sequence[str], None] = "b55cce9cc203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "stock_inbound_record",
        sa.Column("supplier", sa.String(length=255), nullable=True, comment="供应商"),
    )
    op.add_column(
        "stock_inbound_record",
        sa.Column("warranty_period", sa.String(length=255), nullable=True, comment="维保期"),
    )


def downgrade() -> None:
    op.drop_column("stock_inbound_record", "warranty_period")
    op.drop_column("stock_inbound_record", "supplier")
