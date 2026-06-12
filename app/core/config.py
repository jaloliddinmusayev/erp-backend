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

    # CORS — comma-separated origins; override via CORS_ORIGINS env on the server
    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "https://erp-admin-five.vercel.app,"
        "https://triad.uz,"
        "https://www.triad.uz"
    )
    # Vercel preview + triad.uz custom domain (with or without www)
    cors_allow_origin_regex: str = r"https://(www\.)?triad\.uz|https://.*\.vercel\.app"

    # --- WMS outbound (worker + HttpWmsClient) ---
    wms_mock_mode: bool = True
    wms_base_url: str = ""
    wms_api_key: str = ""
    wms_http_timeout_seconds: float = 30.0

    # --- Integration worker (scripts/run_worker.py) ---
    integration_job_max_attempts: int = 5
    integration_worker_batch_size: int = 10
    integration_job_stale_processing_seconds: int = 900
    integration_worker_loop_seconds: int = 0  # 0 = single cycle then exit; >0 = daemon loop


def parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
