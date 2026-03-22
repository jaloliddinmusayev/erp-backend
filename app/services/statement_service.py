"""
Client AR statement: cash-basis running balance (invoices vs payments).

- Posting lines: invoice_issued (debit), payment_received (credit).
- payment_allocated rows are non-posting audit notes (debit/credit 0) so managers see
  how receipts were applied without double-counting against the running balance.

Closing balance matches: opening + invoice debits − payment credits in the window (excluding memo lines).
It may differ from sum(invoice.outstanding) when unallocated payments exist; use aging for open-invoice truth.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.money import quantize_money
from app.models.client import Client
from app.models.invoice import Invoice, InvoiceStatus, PaymentAllocation
from app.models.payment import Payment
from app.schemas.payment import ClientBriefPayment
from app.schemas.receivable import ClientStatementResponse, StatementLineResponse, StatementLineType


def _get_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def _countable_invoice(inv: Invoice) -> bool:
    return inv.is_active and inv.status not in (InvoiceStatus.draft, InvoiceStatus.cancelled)


@dataclass(frozen=True)
class _StmtEvent:
    sort_date: date
    sort_order: int
    tie_id: int


def get_client_statement(
    db: Session,
    company_id: int,
    client_id: int,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ClientStatementResponse:
    client = _get_client(db, company_id, client_id)

    today = date.today()
    if date_from is not None and date_to is not None and date_from > date_to:
        raise BusinessRuleError("date_from must be on or before date_to.")

    eff_from = date_from
    eff_to = date_to if date_to is not None else (today if date_from is not None else None)

    # Opening: only when a start boundary exists
    opening = Decimal("0")
    if eff_from is not None:
        inv_before = db.scalars(
            select(Invoice).where(
                Invoice.company_id == company_id,
                Invoice.client_id == client_id,
                Invoice.is_active.is_(True),
                Invoice.status.not_in((InvoiceStatus.draft, InvoiceStatus.cancelled)),
                Invoice.invoice_date < eff_from,
            )
        ).all()
        pay_before = db.scalars(
            select(Payment).where(
                Payment.company_id == company_id,
                Payment.client_id == client_id,
                Payment.is_active.is_(True),
                Payment.payment_date < eff_from,
            )
        ).all()
        deb = quantize_money(sum((i.total_amount for i in inv_before), Decimal("0")))
        cr = quantize_money(sum((p.amount for p in pay_before), Decimal("0")))
        opening = quantize_money(deb - cr)

    # Load movements
    inv_q = select(Invoice).where(
        Invoice.company_id == company_id,
        Invoice.client_id == client_id,
    )
    pay_q = select(Payment).where(
        Payment.company_id == company_id,
        Payment.client_id == client_id,
    )
    alloc_q = (
        select(PaymentAllocation)
        .join(Payment, PaymentAllocation.payment_id == Payment.id)
        .options(joinedload(PaymentAllocation.invoice), joinedload(PaymentAllocation.payment))
        .where(
            PaymentAllocation.company_id == company_id,
            PaymentAllocation.is_active.is_(True),
            Payment.client_id == client_id,
        )
    )

    invoices = list(db.scalars(inv_q).all())
    payments = list(db.scalars(pay_q).all())
    allocations = list(db.scalars(alloc_q).unique().all())

    raw_lines: list[tuple[_StmtEvent, StatementLineResponse]] = []

    for inv in invoices:
        if not _countable_invoice(inv):
            continue
        d = inv.invoice_date
        if eff_from is not None and d < eff_from:
            continue
        if eff_to is not None and d > eff_to:
            continue
        amt = quantize_money(inv.total_amount)
        raw_lines.append(
            (
                _StmtEvent(d, 0, inv.id),
                StatementLineResponse(
                    date=d,
                    type=StatementLineType.invoice_issued,
                    reference=inv.invoice_number,
                    description=f"Invoice {inv.invoice_number}",
                    debit_amount=amt,
                    credit_amount=Decimal("0"),
                    running_balance=Decimal("0"),
                ),
            )
        )

    for pay in payments:
        if not pay.is_active:
            continue
        d = pay.payment_date
        if eff_from is not None and d < eff_from:
            continue
        if eff_to is not None and d > eff_to:
            continue
        ref = pay.reference_number or f"PAY-{pay.id}"
        amt = quantize_money(pay.amount)
        raw_lines.append(
            (
                _StmtEvent(d, 1, pay.id),
                StatementLineResponse(
                    date=d,
                    type=StatementLineType.payment_received,
                    reference=ref,
                    description=f"Payment ({pay.payment_method.value})",
                    debit_amount=Decimal("0"),
                    credit_amount=amt,
                    running_balance=Decimal("0"),
                ),
            )
        )

    for alloc in allocations:
        at = alloc.allocated_at
        if at.tzinfo is not None:
            at = at.astimezone(timezone.utc)
        ad = at.date()
        if eff_from is not None and ad < eff_from:
            continue
        if eff_to is not None and ad > eff_to:
            continue
        inv_num = alloc.invoice.invoice_number if alloc.invoice else str(alloc.invoice_id)
        raw_lines.append(
            (
                _StmtEvent(ad, 2, alloc.id),
                StatementLineResponse(
                    date=ad,
                    type=StatementLineType.payment_allocated,
                    reference=f"ALLOC-{alloc.id}",
                    description=(
                        f"Applied {quantize_money(alloc.allocated_amount)} to invoice {inv_num} "
                        f"(payment PAY-{alloc.payment_id})"
                    ),
                    debit_amount=Decimal("0"),
                    credit_amount=Decimal("0"),
                    running_balance=Decimal("0"),
                ),
            )
        )

    raw_lines.sort(key=lambda x: (x[0].sort_date, x[0].sort_order, x[0].tie_id))

    running = opening
    out_lines: list[StatementLineResponse] = []
    for _, line in raw_lines:
        if line.debit_amount != 0 or line.credit_amount != 0:
            running = quantize_money(running + line.debit_amount - line.credit_amount)
        out_lines.append(
            StatementLineResponse(
                date=line.date,
                type=line.type,
                reference=line.reference,
                description=line.description,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                running_balance=running,
            )
        )

    closing = running

    return ClientStatementResponse(
        client=ClientBriefPayment.model_validate(client),
        date_from=eff_from,
        date_to=eff_to,
        opening_balance=opening,
        closing_balance=closing,
        lines=out_lines,
    )
