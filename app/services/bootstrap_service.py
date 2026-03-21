"""
Idempotent initial data (company + admin role + admin user).

Run via `python scripts/seed.py`. Credentials come from ADMIN_EMAIL / ADMIN_PASSWORD (see Settings).
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import hash_password
from app.models.company import Company, TenantMode
from app.models.role import Role
from app.models.user import User

DEMO_COMPANY_NAME = "Core ERP Demo"
DEMO_COMPANY_CODE = "core"
ADMIN_ROLE_CODE = "admin"
ADMIN_ROLE_NAME = "Administrator"


def run_initial_seed(db: Session, *, settings: Settings | None = None) -> dict[str, int | str | bool]:
    """
    Create demo company, admin role, and admin user if missing. Safe to run multiple times.
    Admin user is created only when `admin_email` and `admin_password` are set in settings.
    """
    s = settings or get_settings()
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

    email_raw = (s.admin_email or "").strip()
    password_raw = s.admin_password or ""
    if not email_raw or not password_raw:
        result["user_created"] = False
        result["user_skipped"] = "missing ADMIN_EMAIL or ADMIN_PASSWORD"
        db.commit()
        result["status"] = "ok"
        return result

    email_norm = email_raw.lower()
    user = db.scalars(select(User).where(User.email == email_norm)).first()
    if user is None:
        user = User(
            company_id=company.id,
            role_id=role.id,
            full_name=(s.admin_full_name or "Super Admin").strip() or "Super Admin",
            email=email_norm,
            password_hash=hash_password(password_raw),
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
