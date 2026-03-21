from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    company_id: int | None = Field(
        default=None,
        description="Set for tenant roles; omit/null reserved for future global roles.",
    )
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    is_active: bool = True


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int | None
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
