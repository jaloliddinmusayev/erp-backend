"""clients master

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "code", name="uq_clients_company_code"),
    )
    op.create_index(op.f("ix_clients_company_id"), "clients", ["company_id"], unique=False)
    op.create_index(op.f("ix_clients_code"), "clients", ["code"], unique=False)
    op.create_index(op.f("ix_clients_name"), "clients", ["name"], unique=False)
    op.create_index(op.f("ix_clients_phone"), "clients", ["phone"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_clients_phone"), table_name="clients")
    op.drop_index(op.f("ix_clients_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_code"), table_name="clients")
    op.drop_index(op.f("ix_clients_company_id"), table_name="clients")
    op.drop_table("clients")
