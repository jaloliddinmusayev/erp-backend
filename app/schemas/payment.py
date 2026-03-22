from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.payment import PaymentMethod
from app.models.sales_order import SalesOrderStatus


class ClientBriefPayment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class SalesOrderBriefPayment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: SalesOrderStatus


class UserBriefPayment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class PaymentCreate(BaseModel):
    client_id: int
    sales_order_id: int | None = None
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=4)
    payment_date: date
    payment_method: PaymentMethod
    reference_number: str | None = Field(default=None, max_length=128)
    notes: str | None = None

    @field_validator("reference_number")
    @classmethod
    def strip_ref(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s if s else None


class PaymentResponse(BaseModel):
    id: int
    company_id: int
    client_id: int
    sales_order_id: int | None
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    reference_number: str | None
    notes: str | None
    is_active: bool
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime
    client: ClientBriefPayment
    sales_order: SalesOrderBriefPayment | None
    created_by_user: UserBriefPayment | None


class ClientReceivableResponse(BaseModel):
    client_id: int
    company_id: int
    client: ClientBriefPayment
    total_sales_amount: Decimal
    total_paid_amount: Decimal
    outstanding_amount: Decimal


class SalesOrderPaymentSummaryResponse(BaseModel):
    sales_order_id: int
    company_id: int
    client_id: int
    order_number: str
    status: SalesOrderStatus
    order_total_amount: Decimal
    total_paid_amount: Decimal
    outstanding_amount: Decimal


def payment_to_response(p) -> PaymentResponse:
    so = None
    if p.sales_order_id is not None and p.sales_order is not None:
        so = SalesOrderBriefPayment.model_validate(p.sales_order)
    created_by = None
    if p.created_by_user_id is not None and p.created_by_user is not None:
        created_by = UserBriefPayment.model_validate(p.created_by_user)
    return PaymentResponse(
        id=p.id,
        company_id=p.company_id,
        client_id=p.client_id,
        sales_order_id=p.sales_order_id,
        amount=p.amount,
        payment_date=p.payment_date,
        payment_method=p.payment_method,
        reference_number=p.reference_number,
        notes=p.notes,
        is_active=p.is_active,
        created_by_user_id=p.created_by_user_id,
        created_at=p.created_at,
        updated_at=p.updated_at,
        client=ClientBriefPayment.model_validate(p.client),
        sales_order=so,
        created_by_user=created_by,
    )
