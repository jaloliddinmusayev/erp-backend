"""sales orders + line items

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=True),
        sa.Column("order_number", sa.String(length=64), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "order_number", name="uq_sales_orders_company_order_number"),
    )
    op.create_index(op.f("ix_sales_orders_branch_id"), "sales_orders", ["branch_id"], unique=False)
    op.create_index(op.f("ix_sales_orders_client_id"), "sales_orders", ["client_id"], unique=False)
    op.create_index(op.f("ix_sales_orders_company_id"), "sales_orders", ["company_id"], unique=False)
    op.create_index(op.f("ix_sales_orders_order_date"), "sales_orders", ["order_date"], unique=False)
    op.create_index(op.f("ix_sales_orders_order_number"), "sales_orders", ["order_number"], unique=False)
    op.create_index(op.f("ix_sales_orders_status"), "sales_orders", ["status"], unique=False)

    op.create_table(
        "sales_order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sales_order_items_company_id"), "sales_order_items", ["company_id"], unique=False)
    op.create_index(op.f("ix_sales_order_items_product_id"), "sales_order_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_sales_order_items_sales_order_id"), "sales_order_items", ["sales_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sales_order_items_sales_order_id"), table_name="sales_order_items")
    op.drop_index(op.f("ix_sales_order_items_product_id"), table_name="sales_order_items")
    op.drop_index(op.f("ix_sales_order_items_company_id"), table_name="sales_order_items")
    op.drop_table("sales_order_items")
    op.drop_index(op.f("ix_sales_orders_status"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_order_number"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_order_date"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_company_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_client_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_branch_id"), table_name="sales_orders")
    op.drop_table("sales_orders")
