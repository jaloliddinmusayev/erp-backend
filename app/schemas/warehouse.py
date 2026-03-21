from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseCreate(BaseModel):
    company_id: int
    branch_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=64)
    address: str | None = None
    is_active: bool = True


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    branch_id: int
    name: str
    code: str
    address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
