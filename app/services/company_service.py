from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.company import Company
from app.schemas.company import CompanyCreate


def create_company(db: Session, payload: CompanyCreate) -> Company:
    company = Company(
        name=payload.name.strip(),
        code=payload.code.strip(),
        tenant_mode=payload.tenant_mode,
        is_active=payload.is_active,
    )
    db.add(company)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Company code already exists.") from None
    db.refresh(company)
    return company


def list_companies(db: Session, *, skip: int = 0, limit: int = 100) -> list[Company]:
    stmt = select(Company).order_by(Company.id).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).all())


def list_companies_for_tenant(db: Session, *, company_id: int) -> list[Company]:
    company = db.get(Company, company_id)
    return [company] if company is not None else []
