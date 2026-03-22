import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.company import Company
    from app.models.payment import Payment
    from app.models.product import Product
    from app.models.sales_order import SalesOrder
    from app.models.user import User


class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    issued = "issued"
    partially_paid = "partially_paid"
    paid = "paid"
    cancelled = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("company_id", "invoice_number", name="uq_invoices_company_invoice_number"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    sales_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=InvoiceStatus.draft,
        server_default=InvoiceStatus.draft.value,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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

    company: Mapped["Company"] = relationship(back_populates="invoices")
    client: Mapped["Client"] = relationship(back_populates="invoices")
    sales_order: Mapped["SalesOrder | None"] = relationship(back_populates="invoices")
    created_by_user: Mapped["User | None"] = relationship(back_populates="invoices_created")
    items: Mapped[list["InvoiceItem"]] = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    payment_allocations: Mapped[list["PaymentAllocation"]] = relationship(
        "PaymentAllocation",
        back_populates="invoice",
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_code: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
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

    company: Mapped["Company"] = relationship(back_populates="invoice_items")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    product: Mapped["Product | None"] = relationship(back_populates="invoice_items")


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False, index=True)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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

    company: Mapped["Company"] = relationship(back_populates="payment_allocations")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payment_allocations")
    created_by_user: Mapped["User | None"] = relationship(back_populates="payment_allocations_created")
