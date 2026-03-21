"""
FastAPI dependencies.

Future JWT phase: add `get_current_user`, `get_current_company_id` derived from token
and stop accepting raw `company_id` query params on tenant-scoped list endpoints.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
