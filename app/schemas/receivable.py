from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.payment import ClientBriefPayment


class StatementLineType(str, Enum):
    invoice_issued = "invoice_issued"
    payment_received = "payment_received"
    payment_allocated = "payment_allocated"
    adjustment_placeholder = "adjustment_placeholder"


class AgingBucket(str, Enum):
    current = "current"
    days_1_30 = "days_1_30"
    days_31_60 = "days_31_60"
    days_61_90 = "days_61_90"
    days_90_plus = "days_90_plus"


class StatementLineResponse(BaseModel):
    date: date
    type: StatementLineType
    reference: str
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    running_balance: Decimal


class ClientStatementResponse(BaseModel):
    client: ClientBriefPayment
    date_from: date | None
    date_to: date | None
    opening_balance: Decimal
    closing_balance: Decimal
    lines: list[StatementLineResponse]


class AgingBucketSummaryResponse(BaseModel):
    total_outstanding: Decimal
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_90_plus: Decimal


class InvoiceAgingDetailResponse(BaseModel):
    invoice_id: int
    invoice_number: str
    invoice_date: date
    due_date: date | None
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    overdue_days: int
    aging_bucket: AgingBucket
    is_overdue: bool


class ClientAgingResponse(BaseModel):
    client: ClientBriefPayment
    summary: AgingBucketSummaryResponse
    invoices: list[InvoiceAgingDetailResponse] = Field(default_factory=list)


class GlobalAgingResponse(BaseModel):
    as_of_date: date
    summary: AgingBucketSummaryResponse
