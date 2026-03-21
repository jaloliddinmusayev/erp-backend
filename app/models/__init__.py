"""
Import all models here so Alembic `target_metadata` and migrations stay in sync.

Future modules (procurement, finance): add files and re-export below.
"""

from app.models.branch import Branch
from app.models.category import Category
from app.models.client import Client
from app.models.company import Company, TenantMode
from app.models.product import Product
from app.models.role import Role
from app.models.sales_order import FulfillmentStatus, SalesOrder, SalesOrderItem, SalesOrderStatus
from app.models.unit import Unit
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "Branch",
    "Category",
    "Client",
    "Company",
    "Product",
    "Role",
    "FulfillmentStatus",
    "SalesOrder",
    "SalesOrderItem",
    "SalesOrderStatus",
    "TenantMode",
    "Unit",
    "User",
    "Warehouse",
]
