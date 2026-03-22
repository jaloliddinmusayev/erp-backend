from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.money import quantize_money
from app.models.invoice import Invoice, InvoiceStatus, PaymentAllocation
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import ClientBriefPayment
from app.schemas.payment_allocation import (
    InvoiceBriefAllocation,
    PaymentAllocationCreate,
    PaymentAllocationResponse,
    PaymentNestedAllocation,
    UserBriefAllocation,
)


def recalculate_invoice_balances(db: Session, company_id: int, invoice_id: int) -> None:
    inv = db.get(Invoice, invoice_id)
    if inv is None or inv.company_id != company_id:
        raise NotFoundError("Invoice not found.")
    if inv.status == InvoiceStatus.cancelled:
        return
    if inv.status == InvoiceStatus.draft:
        inv.paid_amount = Decimal("0")
        inv.outstanding_amount = Decimal("0")
        return

    total_paid = db.scalar(
        select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.invoice_id == invoice_id,
            PaymentAllocation.company_id == company_id,
            PaymentAllocation.is_active.is_(True),
        )
    )
    paid = quantize_money(Decimal(str(total_paid or 0)))
    inv.paid_amount = paid
    out = quantize_money(inv.total_amount - paid)
    if out < 0:
        out = Decimal("0")
    inv.outstanding_amount = out

    if inv.outstanding_amount <= 0:
        inv.status = InvoiceStatus.paid
    elif paid > 0:
        inv.status = InvoiceStatus.partially_paid
    else:
        inv.status = InvoiceStatus.issued


def _get_payment_for_allocation(db: Session, company_id: int, payment_id: int) -> Payment:
    stmt = (
        select(Payment)
        .options(joinedload(Payment.client))
        .where(Payment.id == payment_id, Payment.company_id == company_id)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Payment not found.")
    return row


def _get_invoice_for_allocation(db: Session, company_id: int, invoice_id: int) -> Invoice:
    row = db.get(Invoice, invoice_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Invoice not found.")
    return row


def get_payment_total_allocated_amount(db: Session, company_id: int, payment_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.payment_id == payment_id,
            PaymentAllocation.company_id == company_id,
            PaymentAllocation.is_active.is_(True),
        )
    )
    return quantize_money(Decimal(str(total or 0)))


def get_payment_unallocated_amount(db: Session, company_id: int, payment_id: int) -> Decimal:
    pay = _get_payment_for_allocation(db, company_id, payment_id)
    if not pay.is_active:
        return Decimal("0")
    alloc = get_payment_total_allocated_amount(db, company_id, payment_id)
    return quantize_money(quantize_money(pay.amount) - alloc)


def create_payment_allocation(
    db: Session,
    company_id: int,
    payload: PaymentAllocationCreate,
    *,
    created_by_user_id: int,
) -> PaymentAllocation:
    pay = _get_payment_for_allocation(db, company_id, payload.payment_id)
    inv = _get_invoice_for_allocation(db, company_id, payload.invoice_id)

    if not pay.is_active:
        raise BusinessRuleError("Cannot allocate from an inactive payment.")
    if not inv.is_active:
        raise BusinessRuleError("Cannot allocate to an inactive invoice.")
    if inv.status == InvoiceStatus.cancelled:
        raise BusinessRuleError("Cannot allocate to a cancelled invoice.")
    if inv.status == InvoiceStatus.draft:
        raise BusinessRuleError("Cannot allocate to a draft invoice; issue the invoice first.")

    if pay.client_id != inv.client_id:
        raise BusinessRuleError("Payment and invoice must belong to the same client.")

    user = db.get(User, created_by_user_id)
    if user is None or user.company_id != company_id:
        raise NotFoundError("User not found.")

    amount = quantize_money(payload.allocated_amount)
    unalloc = get_payment_unallocated_amount(db, company_id, pay.id)
    if amount > unalloc:
        raise BusinessRuleError("Allocation exceeds unallocated payment amount.")
    outstanding = quantize_money(inv.outstanding_amount)
    if amount > outstanding:
        raise BusinessRuleError("Allocation exceeds invoice outstanding amount.")

    row = PaymentAllocation(
        company_id=company_id,
        payment_id=pay.id,
        invoice_id=inv.id,
        allocated_amount=amount,
        notes=payload.notes,
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(row)
    db.flush()
    recalculate_invoice_balances(db, company_id, inv.id)
    db.commit()

    stmt = (
        select(PaymentAllocation)
        .options(
            joinedload(PaymentAllocation.payment),
            joinedload(PaymentAllocation.invoice),
            joinedload(PaymentAllocation.created_by_user),
        )
        .where(PaymentAllocation.id == row.id)
    )
    return db.scalars(stmt).one()


def list_payment_allocations(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    payment_id: int | None = None,
    invoice_id: int | None = None,
    is_active: bool | None = None,
) -> list[PaymentAllocation]:
    stmt = (
        select(PaymentAllocation)
        .options(
            joinedload(PaymentAllocation.payment).joinedload(Payment.client),
            joinedload(PaymentAllocation.invoice),
            joinedload(PaymentAllocation.created_by_user),
        )
        .where(PaymentAllocation.company_id == company_id)
    )
    if payment_id is not None:
        stmt = stmt.where(PaymentAllocation.payment_id == payment_id)
    if invoice_id is not None:
        stmt = stmt.where(PaymentAllocation.invoice_id == invoice_id)
    if is_active is not None:
        stmt = stmt.where(PaymentAllocation.is_active == is_active)
    stmt = stmt.order_by(PaymentAllocation.allocated_at.desc(), PaymentAllocation.id.desc()).offset(skip).limit(
        min(limit, 500)
    )
    return list(db.scalars(stmt).unique().all())


def get_payment_allocation(db: Session, company_id: int, allocation_id: int) -> PaymentAllocation:
    stmt = (
        select(PaymentAllocation)
        .options(
            joinedload(PaymentAllocation.payment).joinedload(Payment.client),
            joinedload(PaymentAllocation.invoice),
            joinedload(PaymentAllocation.created_by_user),
        )
        .where(PaymentAllocation.id == allocation_id, PaymentAllocation.company_id == company_id)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Payment allocation not found.")
    return row


def deactivate_payment_allocation(db: Session, company_id: int, allocation_id: int) -> PaymentAllocation:
    row = get_payment_allocation(db, company_id, allocation_id)
    inv_id = row.invoice_id
    if not row.is_active:
        return row
    row.is_active = False
    db.flush()
    recalculate_invoice_balances(db, company_id, inv_id)
    db.commit()
    return get_payment_allocation(db, company_id, allocation_id)


def payment_allocation_to_response(row: PaymentAllocation) -> PaymentAllocationResponse:
    client = ClientBriefPayment.model_validate(row.payment.client)
    inv = InvoiceBriefAllocation(
        id=row.invoice.id,
        invoice_number=row.invoice.invoice_number,
        status=row.invoice.status,
    )
    pay_nested = PaymentNestedAllocation(
        id=row.payment.id,
        amount=row.payment.amount,
        payment_date=row.payment.payment_date,
    )
    created_by = None
    if row.created_by_user_id is not None and row.created_by_user is not None:
        created_by = UserBriefAllocation.model_validate(row.created_by_user)
    return PaymentAllocationResponse(
        id=row.id,
        company_id=row.company_id,
        payment_id=row.payment_id,
        invoice_id=row.invoice_id,
        allocated_amount=row.allocated_amount,
        allocated_at=row.allocated_at,
        notes=row.notes,
        is_active=row.is_active,
        created_by_user_id=row.created_by_user_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        client=client,
        invoice=inv,
        payment=pay_nested,
        created_by_user=created_by,
    )
