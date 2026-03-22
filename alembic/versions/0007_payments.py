"""manual payments (client receivables foundation)

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(length=32), nullable=False),
        sa.Column("reference_number", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_company_id"), "payments", ["company_id"], unique=False)
    op.create_index(op.f("ix_payments_client_id"), "payments", ["client_id"], unique=False)
    op.create_index(op.f("ix_payments_sales_order_id"), "payments", ["sales_order_id"], unique=False)
    op.create_index(op.f("ix_payments_payment_date"), "payments", ["payment_date"], unique=False)
    op.create_index(op.f("ix_payments_payment_method"), "payments", ["payment_method"], unique=False)
    op.create_index(op.f("ix_payments_created_by_user_id"), "payments", ["created_by_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_created_by_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_method"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_date"), table_name="payments")
    op.drop_index(op.f("ix_payments_sales_order_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_client_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_company_id"), table_name="payments")
    op.drop_table("payments")
