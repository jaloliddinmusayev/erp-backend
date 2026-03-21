from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.branch import Branch
from app.models.company import Company
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate


def _get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise NotFoundError("Company not found.")
    return company


def create_warehouse(db: Session, payload: WarehouseCreate) -> Warehouse:
    _get_company(db, payload.company_id)
    branch = db.get(Branch, payload.branch_id)
    if branch is None:
        raise NotFoundError("Branch not found.")
    if branch.company_id != payload.company_id:
        raise ConflictError("Branch does not belong to the given company.")

    warehouse = Warehouse(
        company_id=payload.company_id,
        branch_id=payload.branch_id,
        name=payload.name.strip(),
        code=payload.code.strip(),
        address=payload.address,
        is_active=payload.is_active,
    )
    db.add(warehouse)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Warehouse code already exists for this company.") from None
    db.refresh(warehouse)
    return warehouse


def list_warehouses_by_company(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[Warehouse]:
    _get_company(db, company_id)
    stmt = (
        select(Warehouse)
        .where(Warehouse.company_id == company_id)
        .order_by(Warehouse.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())
