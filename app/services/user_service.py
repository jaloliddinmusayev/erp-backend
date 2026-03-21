from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def _get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise NotFoundError("Company not found.")
    return company


def create_user(db: Session, payload: UserCreate) -> User:
    _get_company(db, payload.company_id)
    role = db.get(Role, payload.role_id)
    if role is None:
        raise NotFoundError("Role not found.")
    if role.company_id is not None and role.company_id != payload.company_id:
        raise ConflictError("Role does not belong to the given company.")

    user = User(
        company_id=payload.company_id,
        role_id=payload.role_id,
        full_name=payload.full_name.strip(),
        email=str(payload.email).lower().strip(),
        password_hash=hash_password(payload.password),
        is_active=payload.is_active,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Email already registered.") from None
    db.refresh(user)
    return user


def list_users_by_company(db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> list[User]:
    _get_company(db, company_id)
    stmt = (
        select(User)
        .where(User.company_id == company_id)
        .order_by(User.id)
        .offset(skip)
        .limit(min(limit, 500))
    )
    return list(db.scalars(stmt).all())
