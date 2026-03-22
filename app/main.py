"""
Core ERP API — phase 1 foundation.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    auth,
    branches,
    categories,
    clients,
    companies,
    integration_jobs,
    invoices,
    payment_allocations,
    payments,
    products,
    receivables,
    roles,
    sales_orders,
    units,
    users,
    warehouses,
    wms,
)
from app.core.config import get_settings
from app.core.lifecycle import run_startup_hooks

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_hooks(settings)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(branches.router, prefix="/branches", tags=["branches"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(units.router, prefix="/units", tags=["units"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(sales_orders.router, prefix="/sales-orders", tags=["sales-orders"])
app.include_router(integration_jobs.router, prefix="/integration-jobs", tags=["integration-jobs"])
app.include_router(wms.router, prefix="/wms", tags=["wms"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(
    payment_allocations.router,
    prefix="/payment-allocations",
    tags=["payment-allocations"],
)
app.include_router(receivables.router, prefix="/receivables", tags=["receivables"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Core ERP API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
