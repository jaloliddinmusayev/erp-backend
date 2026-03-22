from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.invoice import InvoiceStatus
from app.schemas.payment import ClientBriefPayment, SalesOrderBriefPayment


class UserBriefInvoice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class InvoiceItemCreate(BaseModel):
    product_id: int | None = None
    product_code: str | None = Field(default=None, max_length=64)
    product_name: str | None = Field(default=None, max_length=255)
    quantity: Decimal = Field(..., gt=0, max_digits=18, decimal_places=4)
    unit_price: Decimal = Field(..., ge=0, max_digits=18, decimal_places=4)
    notes: str | None = None

    @model_validator(mode="after")
    def require_identity(self) -> "InvoiceItemCreate":
        if self.product_id is None:
            code = (self.product_code or "").strip()
            name = (self.product_name or "").strip()
            if not code or not name:
                raise ValueError("Without product_id, product_code and product_name are required.")
            self.product_code = code
            self.product_name = name
        return self


class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    invoice_id: int
    product_id: int | None
    product_code: str
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime


class InvoiceCreate(BaseModel):
    client_id: int
    sales_order_id: int | None = None
    invoice_number: str = Field(..., min_length=1, max_length=64)
    invoice_date: date
    due_date: date | None = None
    notes: str | None = None
    items: list[InvoiceItemCreate] = Field(..., min_length=1)

    @field_validator("invoice_number")
    @classmethod
    def strip_invoice_number(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("invoice_number cannot be empty")
        return s


class InvoiceFromSalesOrderCreate(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=64)
    invoice_date: date
    due_date: date | None = None
    notes: str | None = None

    @field_validator("invoice_number")
    @classmethod
    def strip_invoice_number(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("invoice_number cannot be empty")
        return s


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = Field(default=None, min_length=1, max_length=64)
    invoice_date: date | None = None
    due_date: date | None = None
    notes: str | None = None
    items: list[InvoiceItemCreate] | None = None

    @field_validator("invoice_number")
    @classmethod
    def strip_invoice_number(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("invoice_number cannot be empty")
        return s


class AllocationsSummaryResponse(BaseModel):
    active_allocation_count: int
    total_allocated_amount: Decimal


class InvoiceResponse(BaseModel):
    id: int
    company_id: int
    client_id: int
    sales_order_id: int | None
    invoice_number: str
    invoice_date: date
    due_date: date | None
    status: InvoiceStatus
    notes: str | None
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    is_active: bool
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime
    client: ClientBriefPayment
    sales_order: SalesOrderBriefPayment | None
    items: list[InvoiceItemResponse]
    allocations_summary: AllocationsSummaryResponse
    created_by_user: UserBriefInvoice | None


class InvoiceSummaryResponse(BaseModel):
    id: int
    company_id: int
    client_id: int
    sales_order_id: int | None
    invoice_number: str
    invoice_date: date
    due_date: date | None
    status: InvoiceStatus
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    is_active: bool
    created_at: datetime
    client: ClientBriefPayment
    sales_order: SalesOrderBriefPayment | None
