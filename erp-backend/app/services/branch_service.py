from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.branch import Branch
from app.models.company import Company
from app.schemas.branch import BranchCreate


def _get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise NotFoundError("Company not found.")
    return company


def create_branch(db: Session, payload: BranchCreate) -> Branch:
    _get_company(db, payload.company_id)
    branch = Branch(
        company_id=payload.company_id,
        name=payload.name.strip(),
        code=payload.code.strip(),
        address=payload.address,
        is_active=payload.is_active,
    )
    db.add(branch)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Branch code already exists for this company.") from None
    db.refresh(branch)
    return branch


def list_branches_by_company(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[Branch]:
    _get_company(db, company_id)
    stmt = (
        select(Branch)
        .where(Branch.company_id == company_id)
        .order_by(Branch.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())
