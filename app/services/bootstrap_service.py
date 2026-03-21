"""
Idempotent initial data for first login (company + admin role + super admin user).

Run via `python scripts/seed.py` from repo root — not on every app startup (avoids races on multi-instance deploys).
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.company import Company, TenantMode
from app.models.role import Role
from app.models.user import User

DEMO_COMPANY_NAME = "Core ERP Demo"
DEMO_COMPANY_CODE = "core"
ADMIN_ROLE_CODE = "admin"
ADMIN_ROLE_NAME = "Administrator"
SEED_ADMIN_EMAIL = "admin@erp.uz"
SEED_ADMIN_NAME = "Super Admin"
SEED_ADMIN_PASSWORD = "123456"


def run_initial_seed(db: Session) -> dict[str, int | str | bool]:
    """
    Create demo company, admin role, and seed user if missing. Safe to run multiple times.
    Returns ids and status flags for logging.
    """
    result: dict[str, int | str | bool] = {"status": "noop"}

    company = db.scalars(select(Company).where(Company.code == DEMO_COMPANY_CODE)).first()
    if company is None:
        company = Company(
            name=DEMO_COMPANY_NAME,
            code=DEMO_COMPANY_CODE,
            tenant_mode=TenantMode.shared,
            is_active=True,
        )
        db.add(company)
        db.flush()
        result["company_created"] = True
    else:
        result["company_created"] = False
    result["company_id"] = company.id

    role = db.scalars(
        select(Role).where(Role.company_id == company.id, Role.code == ADMIN_ROLE_CODE)
    ).first()
    if role is None:
        role = Role(
            company_id=company.id,
            code=ADMIN_ROLE_CODE,
            name=ADMIN_ROLE_NAME,
            description="Full access within company tenant",
            is_active=True,
        )
        db.add(role)
        db.flush()
        result["role_created"] = True
    else:
        result["role_created"] = False
    result["role_id"] = role.id

    email_norm = SEED_ADMIN_EMAIL.lower().strip()
    user = db.scalars(select(User).where(User.email == email_norm)).first()
    if user is None:
        user = User(
            company_id=company.id,
            role_id=role.id,
            full_name=SEED_ADMIN_NAME,
            email=email_norm,
            password_hash=hash_password(SEED_ADMIN_PASSWORD),
            is_active=True,
        )
        db.add(user)
        db.flush()
        result["user_created"] = True
    else:
        result["user_created"] = False
    result["user_id"] = user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    result["status"] = "ok"
    return result
