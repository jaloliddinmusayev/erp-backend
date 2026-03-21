"""
Core ERP API — phase 1 foundation.

Future: WMS integration via outbound HTTP clients; keep domain logic isolated here.
"""

from fastapi import FastAPI

from app.api.routes import branches, companies, roles, users, warehouses
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(branches.router, prefix="/branches", tags=["branches"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Core ERP API is running"}
