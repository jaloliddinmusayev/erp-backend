import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.company import Company

ENTITY_TYPE_SALES_ORDER = "sales_order"
EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER = "wms.outbound.sales_order"


class IntegrationJobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    sent = "sent"
    failed = "failed"


class IntegrationJob(Base):
    """Outbox-style row for async outbound integration (e.g. future WMS worker)."""

    __tablename__ = "integration_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IntegrationJobStatus] = mapped_column(
        SQLEnum(IntegrationJobStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=IntegrationJobStatus.pending,
        server_default=IntegrationJobStatus.pending.value,
        index=True,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    company: Mapped["Company"] = relationship(back_populates="integration_jobs")
