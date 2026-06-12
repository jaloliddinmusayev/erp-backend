import re
from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.client import ClientType

_PHONE_RE = re.compile(r"^(\+998|998)?[0-9]{9}$")
_INN_LEGAL_RE = re.compile(r"^\d{9}$")
_INN_INDIVIDUAL_RE = re.compile(r"^\d{14}$")
_MFO_RE = re.compile(r"^\d{5}$")
_BANK_ACCOUNT_RE = re.compile(r"^\d{5,32}$")


class ClientCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    client_type: ClientType = ClientType.legal_entity
    inn: str = Field(..., min_length=1, max_length=14)
    legal_name: str | None = Field(default=None, max_length=255)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = Field(default=None)
    region: str | None = Field(default=None, max_length=128)
    city: str | None = Field(default=None, max_length=128)
    district: str | None = Field(default=None, max_length=128)
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    bank_name: str | None = Field(default=None, max_length=255)
    bank_account: str | None = Field(default=None, max_length=32)
    bank_mfo: str | None = Field(default=None, max_length=10)
    notes: str | None = None
    is_active: bool = True

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: str, info) -> str:
        digits = re.sub(r"\s", "", v)
        client_type = info.data.get("client_type", ClientType.legal_entity)
        if client_type == ClientType.legal_entity:
            if not _INN_LEGAL_RE.match(digits):
                raise ValueError("INN must be exactly 9 digits for legal entities.")
        elif not _INN_INDIVIDUAL_RE.match(digits):
            raise ValueError("INN must be exactly 14 digits for individuals.")
        return digits

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None or not (s := v.strip()):
            return None
        normalized = re.sub(r"[\s\-()]", "", s)
        if not _PHONE_RE.match(normalized):
            raise ValueError("Phone must be a valid Uzbekistan number.")
        if normalized.startswith("+998"):
            return normalized
        if normalized.startswith("998"):
            return f"+{normalized}"
        return f"+998{normalized}"

    @field_validator("bank_mfo")
    @classmethod
    def validate_mfo(cls, v: str | None) -> str | None:
        if v is None or not (s := v.strip()):
            return None
        if not _MFO_RE.match(s):
            raise ValueError("MFO must be exactly 5 digits.")
        return s

    @field_validator("bank_account")
    @classmethod
    def validate_bank_account(cls, v: str | None) -> str | None:
        if v is None or not (s := v.strip()):
            return None
        if not _BANK_ACCOUNT_RE.match(s):
            raise ValueError("Bank account must contain 5 to 32 digits.")
        return s

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return None
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90.")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return None
        if v < -180 or v > 180:
            raise ValueError("Longitude must be between -180 and 180.")
        return v

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> Self:
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValueError("Latitude and longitude must both be provided or both omitted.")
        return self


class ClientUpdate(ClientCreate):
    pass


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    client_type: ClientType
    inn: str | None
    legal_name: str | None
    contact_person: str | None
    phone: str | None
    email: str | None
    region: str | None
    city: str | None
    district: str | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    bank_name: str | None
    bank_account: str | None
    bank_mfo: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
