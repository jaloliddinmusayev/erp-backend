from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.company import TenantMode


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=64)
    tenant_mode: TenantMode = TenantMode.shared
    is_active: bool = True


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    tenant_mode: TenantMode
    is_active: bool
    created_at: datetime
    updated_at: datetime
