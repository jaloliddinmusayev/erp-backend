from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str


class UnitBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str


class ProductCreate(BaseModel):
    category_id: int
    base_unit_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=64)
    barcode: str | None = Field(default=None, max_length=128)
    description: str | None = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: int
    base_unit_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=64)
    barcode: str | None = Field(default=None, max_length=128)
    description: str | None = None
    is_active: bool = True


class ProductResponse(BaseModel):
    id: int
    company_id: int
    category_id: int
    base_unit_id: int
    name: str
    code: str
    barcode: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryBrief
    base_unit: UnitBrief


def product_to_response(p) -> ProductResponse:
    return ProductResponse(
        id=p.id,
        company_id=p.company_id,
        category_id=p.category_id,
        base_unit_id=p.base_unit_id,
        name=p.name,
        code=p.code,
        barcode=p.barcode,
        description=p.description,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
        category=CategoryBrief.model_validate(p.category),
        base_unit=UnitBrief.model_validate(p.base_unit),
    )
