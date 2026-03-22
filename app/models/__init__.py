"""
Import all models here so Alembic `target_metadata` and migrations stay in sync.

Future modules (procurement, finance): add files and re-export below.
"""

from app.models.branch import Branch
from app.models.category import Category
from app.models.client import Client
from app.models.company import Company, TenantMode
from app.models.integration_job import (
    ENTITY_TYPE_SALES_ORDER,
    EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER,
    IntegrationJob,
    IntegrationJobStatus,
)
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, PaymentAllocation
from app.models.payment import Payment, PaymentMethod
from app.models.product import Product
from app.models.role import Role
from app.models.sales_order import (
    FulfillmentStatus,
    IntegrationStatus,
    SalesOrder,
    SalesOrderItem,
    SalesOrderStatus,
)
from app.models.unit import Unit
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "ENTITY_TYPE_SALES_ORDER",
    "EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER",
    "Branch",
    "Category",
    "Client",
    "Company",
    "FulfillmentStatus",
    "IntegrationJob",
    "IntegrationJobStatus",
    "IntegrationStatus",
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
    "Payment",
    "PaymentAllocation",
    "PaymentMethod",
    "Product",
    "Role",
    "SalesOrder",
    "SalesOrderItem",
    "SalesOrderStatus",
    "TenantMode",
    "Unit",
    "User",
    "Warehouse",
]
