"""
Database engine and declarative base.

Phase 1: single shared PostgreSQL URL from settings.
Future: route sessions to per-company engines when `Company.tenant_mode == dedicated`
(e.g. factory that returns SessionLocal bound to the correct engine for the request).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    echo=_settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
