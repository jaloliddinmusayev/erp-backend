import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum as SQLEnum, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.client import Client
    from app.models.company import Company
    from app.models.product import Product


class SalesOrderStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    sent_to_wms = "sent_to_wms"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class FulfillmentStatus(str, enum.Enum):
    """Aggregate line fulfillment for reporting and future WMS sync."""

    pending = "pending"
    partial = "partial"
    fulfilled = "fulfilled"


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (UniqueConstraint("company_id", "order_number", name="uq_sales_orders_company_order_number"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    order_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[SalesOrderStatus] = mapped_column(
        SQLEnum(SalesOrderStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=SalesOrderStatus.draft,
        server_default=SalesOrderStatus.draft.value,
        index=True,
    )
    fulfillment_status: Mapped[FulfillmentStatus] = mapped_column(
        SQLEnum(FulfillmentStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=FulfillmentStatus.pending,
        server_default=FulfillmentStatus.pending.value,
        index=True,
    )
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_sent_to_wms: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
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

    company: Mapped["Company"] = relationship(back_populates="sales_orders")
    client: Mapped["Client"] = relationship(back_populates="sales_orders")
    branch: Mapped["Branch | None"] = relationship(back_populates="sales_orders")
    items: Mapped[list["SalesOrderItem"]] = relationship(
        back_populates="sales_order",
        cascade="all, delete-orphan",
    )


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    sales_order_id: Mapped[int] = mapped_column(
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    ordered_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fulfilled_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    company: Mapped["Company"] = relationship(back_populates="sales_order_items")
    sales_order: Mapped["SalesOrder"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sales_order_items")
