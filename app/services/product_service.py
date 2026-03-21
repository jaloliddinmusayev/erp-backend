from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.models.unit import Unit
from app.schemas.product import ProductCreate, ProductUpdate


def _normalize_barcode(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return s if s else None


def _ensure_category_company(db: Session, company_id: int, category_id: int) -> Category:
    cat = db.get(Category, category_id)
    if cat is None or cat.company_id != company_id:
        raise NotFoundError("Category not found.")
    return cat


def _ensure_unit_company(db: Session, company_id: int, unit_id: int) -> Unit:
    u = db.get(Unit, unit_id)
    if u is None or u.company_id != company_id:
        raise NotFoundError("Unit not found.")
    return u


def _get_product(db: Session, company_id: int, product_id: int) -> Product:
    stmt = (
        select(Product)
        .options(joinedload(Product.category), joinedload(Product.base_unit))
        .where(Product.id == product_id, Product.company_id == company_id)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Product not found.")
    return row


def create_product(db: Session, company_id: int, payload: ProductCreate) -> Product:
    _ensure_category_company(db, company_id, payload.category_id)
    _ensure_unit_company(db, company_id, payload.base_unit_id)
    barcode = _normalize_barcode(payload.barcode)
    row = Product(
        company_id=company_id,
        category_id=payload.category_id,
        base_unit_id=payload.base_unit_id,
        name=payload.name.strip(),
        code=payload.code.strip(),
        barcode=barcode,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Product code or barcode already exists for this company.") from None
    db.refresh(row)
    stmt = (
        select(Product)
        .options(joinedload(Product.category), joinedload(Product.base_unit))
        .where(Product.id == row.id)
    )
    return db.scalars(stmt).one()


def list_products(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
) -> list[Product]:
    stmt = (
        select(Product)
        .options(joinedload(Product.category), joinedload(Product.base_unit))
        .where(Product.company_id == company_id)
    )
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    stmt = stmt.order_by(Product.id).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).unique().all())


def get_product(db: Session, company_id: int, product_id: int) -> Product:
    return _get_product(db, company_id, product_id)


def update_product(db: Session, company_id: int, product_id: int, payload: ProductUpdate) -> Product:
    row = _get_product(db, company_id, product_id)
    _ensure_category_company(db, company_id, payload.category_id)
    _ensure_unit_company(db, company_id, payload.base_unit_id)
    row.category_id = payload.category_id
    row.base_unit_id = payload.base_unit_id
    row.name = payload.name.strip()
    row.code = payload.code.strip()
    row.barcode = _normalize_barcode(payload.barcode)
    row.description = payload.description
    row.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Product code or barcode already exists for this company.") from None
    db.refresh(row)
    stmt = (
        select(Product)
        .options(joinedload(Product.category), joinedload(Product.base_unit))
        .where(Product.id == row.id)
    )
    return db.scalars(stmt).one()


def deactivate_product(db: Session, company_id: int, product_id: int) -> Product:
    row = _get_product(db, company_id, product_id)
    row.is_active = False
    db.commit()
    db.refresh(row)
    stmt = (
        select(Product)
        .options(joinedload(Product.category), joinedload(Product.base_unit))
        .where(Product.id == row.id)
    )
    return db.scalars(stmt).one()
