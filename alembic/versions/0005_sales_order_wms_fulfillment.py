"""sales order WMS fulfillment fields + item qty rename

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sales_orders",
        sa.Column(
            "fulfillment_status",
            sa.String(length=32),
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column("sales_orders", sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "sales_orders",
        sa.Column("is_sent_to_wms", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index(op.f("ix_sales_orders_fulfillment_status"), "sales_orders", ["fulfillment_status"], unique=False)

    op.execute(sa.text("ALTER TABLE sales_order_items RENAME COLUMN quantity TO ordered_qty"))
    op.add_column(
        "sales_order_items",
        sa.Column("fulfilled_qty", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("sales_order_items", "fulfilled_qty")
    op.execute(sa.text("ALTER TABLE sales_order_items RENAME COLUMN ordered_qty TO quantity"))

    op.drop_index(op.f("ix_sales_orders_fulfillment_status"), table_name="sales_orders")
    op.drop_column("sales_orders", "is_sent_to_wms")
    op.drop_column("sales_orders", "fulfilled_at")
    op.drop_column("sales_orders", "fulfillment_status")
