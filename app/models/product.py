from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.company import Company
    from app.models.invoice import InvoiceItem
    from app.models.sales_order import SalesOrderItem
    from app.models.unit import Unit


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_products_company_code"),
        Index("ix_products_company_name", "company_id", "name"),
        Index(
            "uq_products_company_barcode",
            "company_id",
            "barcode",
            unique=True,
            postgresql_where=text("barcode IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    base_unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    company: Mapped["Company"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")
    base_unit: Mapped["Unit"] = relationship(back_populates="products_as_base")
    sales_order_items: Mapped[list["SalesOrderItem"]] = relationship(back_populates="product")
    invoice_items: Mapped[list["InvoiceItem"]] = relationship(back_populates="product")
