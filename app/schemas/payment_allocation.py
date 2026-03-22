from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.invoice import InvoiceStatus
from app.schemas.payment import ClientBriefPayment


class PaymentAllocationCreate(BaseModel):
    payment_id: int
    invoice_id: int
    allocated_amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=4)
    notes: str | None = None


class InvoiceBriefAllocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    status: InvoiceStatus


class PaymentNestedAllocation(BaseModel):
    id: int
    amount: Decimal
    payment_date: date


class UserBriefAllocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class PaymentAllocationResponse(BaseModel):
    id: int
    company_id: int
    payment_id: int
    invoice_id: int
    allocated_amount: Decimal
    allocated_at: datetime
    notes: str | None
    is_active: bool
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime
    client: ClientBriefPayment
    invoice: InvoiceBriefAllocation
    payment: PaymentNestedAllocation
    created_by_user: UserBriefAllocation | None


class PaymentUnallocatedResponse(BaseModel):
    payment_id: int
    payment_amount: Decimal
    total_allocated_amount: Decimal
    unallocated_amount: Decimal
