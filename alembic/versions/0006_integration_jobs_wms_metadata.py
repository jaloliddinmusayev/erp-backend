"""integration jobs outbox + sales order WMS metadata

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sales_orders", sa.Column("wms_order_id", sa.String(length=128), nullable=True))
    op.add_column(
        "sales_orders",
        sa.Column(
            "integration_status",
            sa.String(length=32),
            nullable=False,
            server_default="not_sent",
        ),
    )
    op.add_column("sales_orders", sa.Column("sent_to_wms_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sales_orders", sa.Column("last_sync_error", sa.Text(), nullable=True))
    op.create_index(op.f("ix_sales_orders_integration_status"), "sales_orders", ["integration_status"], unique=False)
    op.create_index(op.f("ix_sales_orders_wms_order_id"), "sales_orders", ["wms_order_id"], unique=False)

    op.execute(
        sa.text(
            """
            UPDATE sales_orders
            SET integration_status = 'sent'
            WHERE is_sent_to_wms = true
               OR status IN ('sent_to_wms', 'in_progress', 'completed')
            """
        )
    )

    op.create_table(
        "integration_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_integration_jobs_company_id"), "integration_jobs", ["company_id"], unique=False)
    op.create_index(op.f("ix_integration_jobs_entity_type"), "integration_jobs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_integration_jobs_entity_id"), "integration_jobs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_integration_jobs_event_type"), "integration_jobs", ["event_type"], unique=False)
    op.create_index(op.f("ix_integration_jobs_status"), "integration_jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_integration_jobs_status"), table_name="integration_jobs")
    op.drop_index(op.f("ix_integration_jobs_event_type"), table_name="integration_jobs")
    op.drop_index(op.f("ix_integration_jobs_entity_id"), table_name="integration_jobs")
    op.drop_index(op.f("ix_integration_jobs_entity_type"), table_name="integration_jobs")
    op.drop_index(op.f("ix_integration_jobs_company_id"), table_name="integration_jobs")
    op.drop_table("integration_jobs")

    op.drop_index(op.f("ix_sales_orders_wms_order_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_integration_status"), table_name="sales_orders")
    op.drop_column("sales_orders", "last_sync_error")
    op.drop_column("sales_orders", "sent_to_wms_at")
    op.drop_column("sales_orders", "integration_status")
    op.drop_column("sales_orders", "wms_order_id")
