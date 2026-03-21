from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration. Loads from environment and optional `.env` file.

    Future: dedicated-DB mode can resolve engines from `Company.tenant_mode` +
    a connection registry (not implemented in phase 1).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Core ERP API"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/erp_db"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"

    # Bootstrap seed (`scripts/seed.py`) — never commit real passwords to git
    admin_email: str = ""
    admin_password: str = ""
    admin_full_name: str = "Super Admin"

    # Set false if migrations run in CI/release phase only (multi-worker setups)
    run_migrations_on_startup: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
