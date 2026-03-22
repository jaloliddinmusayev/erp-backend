from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.money import quantize_money
from app.models.client import Client
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.payment import ClientBriefPayment
from app.schemas.receivable import (
    AgingBucket,
    AgingBucketSummaryResponse,
    ClientAgingResponse,
    GlobalAgingResponse,
    InvoiceAgingDetailResponse,
)
from app.services.receivable_helpers import (
    bucket_add,
    calculate_invoice_overdue_days,
    determine_aging_bucket,
)


def _get_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def _aging_invoice_query(db: Session, company_id: int, client_id: int | None) -> list[Invoice]:
    stmt = select(Invoice).where(
        Invoice.company_id == company_id,
        Invoice.is_active.is_(True),
        Invoice.status.not_in((InvoiceStatus.draft, InvoiceStatus.cancelled)),
        Invoice.outstanding_amount > 0,
    )
    if client_id is not None:
        stmt = stmt.where(Invoice.client_id == client_id)
    stmt = stmt.order_by(Invoice.invoice_date, Invoice.id)
    return list(db.scalars(stmt).all())


def _empty_buckets() -> dict[AgingBucket, Decimal]:
    return {b: Decimal("0") for b in AgingBucket}


def _summarize_invoices(invoices: list[Invoice], as_of: date) -> AgingBucketSummaryResponse:
    buckets = _empty_buckets()
    total = Decimal("0")
    for inv in invoices:
        o = quantize_money(inv.outstanding_amount)
        total = quantize_money(total + o)
        od = calculate_invoice_overdue_days(inv, as_of)
        b = determine_aging_bucket(od)
        bucket_add(buckets, b, o)
    return AgingBucketSummaryResponse(
        total_outstanding=total,
        current=quantize_money(buckets[AgingBucket.current]),
        days_1_30=quantize_money(buckets[AgingBucket.days_1_30]),
        days_31_60=quantize_money(buckets[AgingBucket.days_31_60]),
        days_61_90=quantize_money(buckets[AgingBucket.days_61_90]),
        days_90_plus=quantize_money(buckets[AgingBucket.days_90_plus]),
    )


def _invoice_to_detail(inv: Invoice, as_of: date) -> InvoiceAgingDetailResponse:
    od = calculate_invoice_overdue_days(inv, as_of)
    b = determine_aging_bucket(od)
    return InvoiceAgingDetailResponse(
        invoice_id=inv.id,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        due_date=inv.due_date,
        total_amount=quantize_money(inv.total_amount),
        paid_amount=quantize_money(inv.paid_amount),
        outstanding_amount=quantize_money(inv.outstanding_amount),
        overdue_days=od,
        aging_bucket=b,
        is_overdue=od > 0,
    )


def get_global_aging_summary(db: Session, company_id: int, *, as_of_date: date | None = None) -> GlobalAgingResponse:
    as_of = as_of_date or date.today()
    rows = _aging_invoice_query(db, company_id, None)
    return GlobalAgingResponse(as_of_date=as_of, summary=_summarize_invoices(rows, as_of))


def get_client_aging_summary(
    db: Session,
    company_id: int,
    client_id: int,
    *,
    as_of_date: date | None = None,
    include_invoices: bool = False,
) -> ClientAgingResponse:
    as_of = as_of_date or date.today()
    client = _get_client(db, company_id, client_id)
    rows = _aging_invoice_query(db, company_id, client_id)
    summary = _summarize_invoices(rows, as_of)
    inv_out: list[InvoiceAgingDetailResponse] = []
    if include_invoices:
        inv_out = [_invoice_to_detail(r, as_of) for r in rows]
    return ClientAgingResponse(
        client=ClientBriefPayment.model_validate(client),
        summary=summary,
        invoices=inv_out,
    )


def list_aging_invoices(
    db: Session,
    company_id: int,
    *,
    client_id: int | None = None,
    as_of_date: date | None = None,
) -> list[InvoiceAgingDetailResponse]:
    if client_id is not None:
        _get_client(db, company_id, client_id)
    as_of = as_of_date or date.today()
    rows = _aging_invoice_query(db, company_id, client_id)
    return [_invoice_to_detail(r, as_of) for r in rows]
