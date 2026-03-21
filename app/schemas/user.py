from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    company_id: int
    role_id: int
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    is_active: bool = True


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    role_id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
