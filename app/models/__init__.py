"""
Import all models here so Alembic `target_metadata` and migrations stay in sync.

Future modules (clients, products, orders, procurement, finance): add files and
re-export below. Keep `company_id` on every tenant-owned table for shared DB;
for dedicated DB, same schema per company DB simplifies migration.
"""

from app.models.branch import Branch
from app.models.category import Category
from app.models.company import Company, TenantMode
from app.models.product import Product
from app.models.role import Role
from app.models.unit import Unit
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "Branch",
    "Category",
    "Company",
    "Product",
    "Role",
    "TenantMode",
    "Unit",
    "User",
    "Warehouse",
]
