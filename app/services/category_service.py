from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _get_category(db: Session, company_id: int, category_id: int) -> Category:
    cat = db.get(Category, category_id)
    if cat is None or cat.company_id != company_id:
        raise NotFoundError("Category not found.")
    return cat


def create_category(db: Session, company_id: int, payload: CategoryCreate) -> Category:
    row = Category(
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
        raise ConflictError("Category code already exists for this company.") from None
    db.refresh(row)
    return row


def list_categories(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[Category]:
    stmt = (
        select(Category)
        .where(Category.company_id == company_id)
        .order_by(Category.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())


def get_category(db: Session, company_id: int, category_id: int) -> Category:
    return _get_category(db, company_id, category_id)


def update_category(db: Session, company_id: int, category_id: int, payload: CategoryUpdate) -> Category:
    row = _get_category(db, company_id, category_id)
    row.name = payload.name.strip()
    row.code = payload.code.strip()
    row.description = payload.description
    row.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Category code already exists for this company.") from None
    db.refresh(row)
    return row


def deactivate_category(db: Session, company_id: int, category_id: int) -> Category:
    row = _get_category(db, company_id, category_id)
    row.is_active = False
    db.commit()
    db.refresh(row)
    return row
