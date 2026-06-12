"""client B2B profile fields

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009"
down_revision: Union[str, Sequence[str], None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column(
            "client_type",
            sa.String(length=32),
            nullable=False,
            server_default="legal_entity",
        ),
    )
    op.add_column("clients", sa.Column("inn", sa.String(length=14), nullable=True))
    op.add_column("clients", sa.Column("legal_name", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("region", sa.String(length=128), nullable=True))
    op.add_column("clients", sa.Column("city", sa.String(length=128), nullable=True))
    op.add_column("clients", sa.Column("district", sa.String(length=128), nullable=True))
    op.add_column("clients", sa.Column("latitude", sa.Numeric(10, 7), nullable=True))
    op.add_column("clients", sa.Column("longitude", sa.Numeric(10, 7), nullable=True))
    op.add_column("clients", sa.Column("bank_name", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("bank_account", sa.String(length=32), nullable=True))
    op.add_column("clients", sa.Column("bank_mfo", sa.String(length=10), nullable=True))
    op.create_index(op.f("ix_clients_inn"), "clients", ["inn"], unique=False)
    op.create_unique_constraint("uq_clients_company_inn", "clients", ["company_id", "inn"])


def downgrade() -> None:
    op.drop_constraint("uq_clients_company_inn", "clients", type_="unique")
    op.drop_index(op.f("ix_clients_inn"), table_name="clients")
    op.drop_column("clients", "bank_mfo")
    op.drop_column("clients", "bank_account")
    op.drop_column("clients", "bank_name")
    op.drop_column("clients", "longitude")
    op.drop_column("clients", "latitude")
    op.drop_column("clients", "district")
    op.drop_column("clients", "city")
    op.drop_column("clients", "region")
    op.drop_column("clients", "legal_name")
    op.drop_column("clients", "inn")
    op.drop_column("clients", "client_type")
