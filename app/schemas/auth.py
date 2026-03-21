from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeRoleOut(BaseModel):
    id: int
    code: str
    name: str


class MeResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    company_id: int
    role: MeRoleOut
