"""invoices, invoice items, payment allocations (AR layer)

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, Sequence[str], None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("invoice_number", sa.String(length=64), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("paid_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("outstanding_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "invoice_number", name="uq_invoices_company_invoice_number"),
    )
    op.create_index(op.f("ix_invoices_company_id"), "invoices", ["company_id"], unique=False)
    op.create_index(op.f("ix_invoices_client_id"), "invoices", ["client_id"], unique=False)
    op.create_index(op.f("ix_invoices_sales_order_id"), "invoices", ["sales_order_id"], unique=False)
    op.create_index(op.f("ix_invoices_invoice_number"), "invoices", ["invoice_number"], unique=False)
    op.create_index(op.f("ix_invoices_invoice_date"), "invoices", ["invoice_date"], unique=False)
    op.create_index(op.f("ix_invoices_status"), "invoices", ["status"], unique=False)
    op.create_index(op.f("ix_invoices_created_by_user_id"), "invoices", ["created_by_user_id"], unique=False)

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("product_code", sa.String(length=64), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_items_company_id"), "invoice_items", ["company_id"], unique=False)
    op.create_index(op.f("ix_invoice_items_invoice_id"), "invoice_items", ["invoice_id"], unique=False)
    op.create_index(op.f("ix_invoice_items_product_id"), "invoice_items", ["product_id"], unique=False)

    op.create_table(
        "payment_allocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("allocated_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("allocated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_payment_allocations_company_id"), "payment_allocations", ["company_id"], unique=False
    )
    op.create_index(
        op.f("ix_payment_allocations_payment_id"), "payment_allocations", ["payment_id"], unique=False
    )
    op.create_index(
        op.f("ix_payment_allocations_invoice_id"), "payment_allocations", ["invoice_id"], unique=False
    )
    op.create_index(
        op.f("ix_payment_allocations_created_by_user_id"),
        "payment_allocations",
        ["created_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_allocations_created_by_user_id"), table_name="payment_allocations")
    op.drop_index(op.f("ix_payment_allocations_invoice_id"), table_name="payment_allocations")
    op.drop_index(op.f("ix_payment_allocations_payment_id"), table_name="payment_allocations")
    op.drop_index(op.f("ix_payment_allocations_company_id"), table_name="payment_allocations")
    op.drop_table("payment_allocations")
    op.drop_index(op.f("ix_invoice_items_product_id"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_invoice_id"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_company_id"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index(op.f("ix_invoices_created_by_user_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_status"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_date"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_sales_order_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_client_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_company_id"), table_name="invoices")
    op.drop_table("invoices")
