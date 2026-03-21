from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate


def _get_unit(db: Session, company_id: int, unit_id: int) -> Unit:
    row = db.get(Unit, unit_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Unit not found.")
    return row


def create_unit(db: Session, company_id: int, payload: UnitCreate) -> Unit:
    row = Unit(
        company_id=company_id,
        name=payload.name.strip(),
        code=payload.code.strip(),
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Unit code already exists for this company.") from None
    db.refresh(row)
    return row


def list_units(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[Unit]:
    stmt = (
        select(Unit)
        .where(Unit.company_id == company_id)
        .order_by(Unit.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())


def get_unit(db: Session, company_id: int, unit_id: int) -> Unit:
    return _get_unit(db, company_id, unit_id)


def update_unit(db: Session, company_id: int, unit_id: int, payload: UnitUpdate) -> Unit:
    row = _get_unit(db, company_id, unit_id)
    row.name = payload.name.strip()
    row.code = payload.code.strip()
    row.description = payload.description
    row.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Unit code already exists for this company.") from None
    db.refresh(row)
    return row


def deactivate_unit(db: Session, company_id: int, unit_id: int) -> Unit:
    row = _get_unit(db, company_id, unit_id)
    row.is_active = False
    db.commit()
    db.refresh(row)
    return row
