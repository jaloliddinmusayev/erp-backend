from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = Field(default=None)
    address: str | None = None
    notes: str | None = None
    is_active: bool = True


class ClientUpdate(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = Field(default=None)
    address: str | None = None
    notes: str | None = None
    is_active: bool = True


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
