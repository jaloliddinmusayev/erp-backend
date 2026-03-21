"""
Startup: logging, DB ping, Alembic upgrade (idempotent `upgrade head`).

Note: With multiple Uvicorn workers, each process runs this once; use 1 worker on small
deployments or disable via RUN_MIGRATIONS_ON_STARTUP=false and run migrations in a release job.
"""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import Settings, get_settings
from app.core.database import engine

logger = logging.getLogger("erp.startup")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _db_log_target(database_url: str) -> str:
    if "@" in database_url:
        return database_url.split("@", 1)[-1][:80]
    return "(configured)"


def check_database_connection(settings: Settings) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection OK (%s)", _db_log_target(settings.database_url))
    except Exception:
        logger.exception("Database connection failed")
        raise


def run_alembic_upgrade_head(settings: Settings) -> None:
    if not ALEMBIC_INI.is_file():
        logger.warning("alembic.ini not found at %s — skipping migrations", ALEMBIC_INI)
        return
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    try:
        command.upgrade(cfg, "head")
        logger.info("Alembic migrations applied (upgrade head — no-op if already current)")
    except Exception:
        logger.exception("Alembic upgrade failed")
        raise


def run_startup_hooks(settings: Settings | None = None) -> None:
    """Synchronous startup sequence (called from FastAPI lifespan)."""
    settings = settings or get_settings()
    configure_logging()
    logger.info("Application starting (%s)", settings.app_name)
    check_database_connection(settings)
    if settings.run_migrations_on_startup:
        run_alembic_upgrade_head(settings)
    else:
        logger.info("RUN_MIGRATIONS_ON_STARTUP=false — skipping Alembic upgrade")
    logger.info("Startup sequence complete")
