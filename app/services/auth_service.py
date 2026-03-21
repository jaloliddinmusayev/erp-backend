from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    stmt = select(User).where(User.email == email.lower().strip())
    user = db.scalars(stmt).first()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
