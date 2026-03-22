from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.money import quantize_money
from app.models.invoice import PaymentAllocation
from app.models.client import Client
from app.models.payment import Payment, PaymentMethod
from app.models.sales_order import SalesOrder, SalesOrderStatus
from app.models.user import User
from app.schemas.payment import (
    ClientBriefPayment,
    ClientReceivableResponse,
    PaymentCreate,
    SalesOrderPaymentSummaryResponse,
)
from app.schemas.payment_allocation import PaymentUnallocatedResponse

def _quantize(value: Decimal) -> Decimal:
    return quantize_money(value)


def _get_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def _get_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    row = db.get(SalesOrder, order_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Sales order not found.")
    return row


def _get_payment(db: Session, company_id: int, payment_id: int) -> Payment:
    stmt = (
        select(Payment)
        .options(
            joinedload(Payment.client),
            joinedload(Payment.sales_order),
            joinedload(Payment.created_by_user),
        )
        .where(Payment.id == payment_id, Payment.company_id == company_id)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Payment not found.")
    return row


def _validate_order_for_payment(order: SalesOrder, client_id: int) -> None:
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot attach a payment to a cancelled sales order.")
    if order.client_id != client_id:
        raise BusinessRuleError("Sales order does not belong to the selected client.")


def create_payment(
    db: Session,
    company_id: int,
    payload: PaymentCreate,
    *,
    created_by_user_id: int,
) -> Payment:
    _get_client(db, company_id, payload.client_id)
    sales_order_id = payload.sales_order_id
    if sales_order_id is not None:
        order = _get_sales_order(db, company_id, sales_order_id)
        _validate_order_for_payment(order, payload.client_id)

    user = db.get(User, created_by_user_id)
    if user is None or user.company_id != company_id:
        raise NotFoundError("User not found.")

    row = Payment(
        company_id=company_id,
        client_id=payload.client_id,
        sales_order_id=sales_order_id,
        amount=quantize_money(payload.amount),
        payment_date=payload.payment_date,
        payment_method=payload.payment_method,
        reference_number=payload.reference_number,
        notes=payload.notes,
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    stmt = (
        select(Payment)
        .options(
            joinedload(Payment.client),
            joinedload(Payment.sales_order),
            joinedload(Payment.created_by_user),
        )
        .where(Payment.id == row.id)
    )
    return db.scalars(stmt).one()


def list_payments(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    client_id: int | None = None,
    sales_order_id: int | None = None,
    payment_method: PaymentMethod | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[Payment]:
    stmt = (
        select(Payment)
        .options(
            joinedload(Payment.client),
            joinedload(Payment.sales_order),
            joinedload(Payment.created_by_user),
        )
        .where(Payment.company_id == company_id)
    )
    if client_id is not None:
        stmt = stmt.where(Payment.client_id == client_id)
    if sales_order_id is not None:
        stmt = stmt.where(Payment.sales_order_id == sales_order_id)
    if payment_method is not None:
        stmt = stmt.where(Payment.payment_method == payment_method)
    if date_from is not None:
        stmt = stmt.where(Payment.payment_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Payment.payment_date <= date_to)
    if is_active is not None:
        stmt = stmt.where(Payment.is_active == is_active)
    if search and (t := search.strip()):
        term = f"%{t}%"
        stmt = stmt.where(or_(Payment.reference_number.ilike(term), Payment.notes.ilike(term)))
    stmt = stmt.order_by(Payment.payment_date.desc(), Payment.id.desc()).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).unique().all())


def get_payment(db: Session, company_id: int, payment_id: int) -> Payment:
    return _get_payment(db, company_id, payment_id)


def deactivate_payment(db: Session, company_id: int, payment_id: int) -> Payment:
    row = _get_payment(db, company_id, payment_id)
    alloc_sum = db.scalar(
        select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.company_id == company_id,
            PaymentAllocation.payment_id == payment_id,
            PaymentAllocation.is_active.is_(True),
        )
    )
    if alloc_sum and Decimal(str(alloc_sum)) > 0:
        raise BusinessRuleError("Cannot deactivate payment with active allocations.")
    row.is_active = False
    db.commit()
    stmt = (
        select(Payment)
        .options(
            joinedload(Payment.client),
            joinedload(Payment.sales_order),
            joinedload(Payment.created_by_user),
        )
        .where(Payment.id == row.id)
    )
    return db.scalars(stmt).one()


def get_payment_unallocated_breakdown(
    db: Session, company_id: int, payment_id: int
) -> PaymentUnallocatedResponse:
    """Return payment amount vs active allocations (for AR UI)."""
    from app.services.payment_allocation_service import (
        get_payment_total_allocated_amount,
        get_payment_unallocated_amount,
    )

    pay = _get_payment(db, company_id, payment_id)
    total_alloc = get_payment_total_allocated_amount(db, company_id, payment_id)
    unalloc = get_payment_unallocated_amount(db, company_id, payment_id)
    return PaymentUnallocatedResponse(
        payment_id=pay.id,
        payment_amount=_quantize(pay.amount),
        total_allocated_amount=total_alloc,
        unallocated_amount=unalloc,
    )


def get_client_receivable_summary(db: Session, company_id: int, client_id: int) -> ClientReceivableResponse:
    client = _get_client(db, company_id, client_id)
    total_sales = db.scalar(
        select(func.coalesce(func.sum(SalesOrder.total_amount), 0)).where(
            SalesOrder.company_id == company_id,
            SalesOrder.client_id == client_id,
            SalesOrder.is_active.is_(True),
            SalesOrder.status != SalesOrderStatus.cancelled,
        )
    )
    total_paid = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.company_id == company_id,
            Payment.client_id == client_id,
            Payment.is_active.is_(True),
        )
    )
    ts = _quantize(Decimal(str(total_sales or 0)))
    tp = _quantize(Decimal(str(total_paid or 0)))
    out = _quantize(ts - tp)
    return ClientReceivableResponse(
        client_id=client.id,
        company_id=company_id,
        client=ClientBriefPayment.model_validate(client),
        total_sales_amount=ts,
        total_paid_amount=tp,
        outstanding_amount=out,
    )


def get_sales_order_payment_summary(
    db: Session, company_id: int, sales_order_id: int
) -> SalesOrderPaymentSummaryResponse:
    order = _get_sales_order(db, company_id, sales_order_id)
    total_paid = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.company_id == company_id,
            Payment.sales_order_id == sales_order_id,
            Payment.is_active.is_(True),
        )
    )
    ot = _quantize(order.total_amount)
    tp = _quantize(Decimal(str(total_paid or 0)))
    out = _quantize(ot - tp)
    return SalesOrderPaymentSummaryResponse(
        sales_order_id=order.id,
        company_id=company_id,
        client_id=order.client_id,
        order_number=order.order_number,
        status=order.status,
        order_total_amount=ot,
        total_paid_amount=tp,
        outstanding_amount=out,
    )
