import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.category import Category
    from app.models.client import Client
    from app.models.product import Product
    from app.models.role import Role
    from app.models.sales_order import SalesOrder, SalesOrderItem
    from app.models.unit import Unit
    from app.models.user import User
    from app.models.warehouse import Warehouse


class TenantMode(str, enum.Enum):
    """How this company's data is hosted; guides future DB routing."""

    shared = "shared"
    dedicated = "dedicated"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    tenant_mode: Mapped[TenantMode] = mapped_column(
        SQLEnum(TenantMode, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=TenantMode.shared,
        server_default=TenantMode.shared.value,
    )
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

    roles: Mapped[list["Role"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    branches: Mapped[list["Branch"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    # Warehouses also hang off `Branch`; DB CASCADE on `company_id` cleans them if company is removed.
    warehouses: Mapped[list["Warehouse"]] = relationship(back_populates="company")
    categories: Mapped[list["Category"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    units: Mapped[list["Unit"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    clients: Mapped[list["Client"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    sales_orders: Mapped[list["SalesOrder"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    sales_order_items: Mapped[list["SalesOrderItem"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
