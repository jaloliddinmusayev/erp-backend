from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.company import Company
from app.models.role import Role
from app.schemas.role import RoleCreate


def _get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise NotFoundError("Company not found.")
    return company


def create_role(db: Session, payload: RoleCreate) -> Role:
    if payload.company_id is not None:
        _get_company(db, payload.company_id)
    role = Role(
        company_id=payload.company_id,
        name=payload.name.strip(),
        code=payload.code.strip(),
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(role)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Role code already exists for this company.") from None
    db.refresh(role)
    return role


def list_roles_by_company(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[Role]:
    _get_company(db, company_id)
    stmt = (
        select(Role)
        .where(Role.company_id == company_id)
        .order_by(Role.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())
