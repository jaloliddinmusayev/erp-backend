from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.money import quantize_money
from app.models.client import Client
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, PaymentAllocation
from app.models.product import Product
from app.models.sales_order import SalesOrder, SalesOrderItem, SalesOrderStatus
from app.models.user import User
from app.schemas.invoice import (
    AllocationsSummaryResponse,
    InvoiceCreate,
    InvoiceFromSalesOrderCreate,
    InvoiceItemCreate,
    InvoiceItemResponse,
    InvoiceResponse,
    InvoiceSummaryResponse,
    InvoiceUpdate,
    UserBriefInvoice,
)
from app.schemas.payment import ClientBriefPayment, SalesOrderBriefPayment

_SO_STATUSES_ALLOWED_FOR_INVOICE: frozenset[SalesOrderStatus] = frozenset(
    {
        SalesOrderStatus.confirmed,
        SalesOrderStatus.sent_to_wms,
        SalesOrderStatus.in_progress,
        SalesOrderStatus.completed,
    }
)


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


def _get_invoice(db: Session, company_id: int, invoice_id: int) -> Invoice:
    stmt = (
        select(Invoice)
        .options(
            joinedload(Invoice.client),
            joinedload(Invoice.sales_order),
            selectinload(Invoice.items),
            selectinload(Invoice.payment_allocations),
            joinedload(Invoice.created_by_user),
        )
        .where(Invoice.id == invoice_id, Invoice.company_id == company_id)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Invoice not found.")
    return row


def _invoice_number_taken(db: Session, company_id: int, invoice_number: str, *, exclude_id: int | None) -> bool:
    stmt = select(Invoice.id).where(
        Invoice.company_id == company_id,
        Invoice.invoice_number == invoice_number,
    )
    if exclude_id is not None:
        stmt = stmt.where(Invoice.id != exclude_id)
    return db.scalar(stmt.limit(1)) is not None


def _validate_order_for_invoice(order: SalesOrder, client_id: int) -> None:
    if order.client_id != client_id:
        raise BusinessRuleError("Sales order does not belong to the selected client.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot invoice a cancelled sales order.")
    if order.status not in _SO_STATUSES_ALLOWED_FOR_INVOICE:
        raise BusinessRuleError(
            "Sales order must be confirmed or later (not draft) to create an invoice from it."
        )


def _resolve_line(
    db: Session,
    company_id: int,
    row: InvoiceItemCreate,
) -> tuple[int | None, str, str, Decimal, Decimal, Decimal, str | None]:
    qty = quantize_money(row.quantity)
    unit_price = quantize_money(row.unit_price)
    if row.product_id is not None:
        prod = db.get(Product, row.product_id)
        if prod is None or prod.company_id != company_id:
            raise NotFoundError("Product not found.")
        code = (row.product_code or "").strip() or prod.code
        name = (row.product_name or "").strip() or prod.name
        pid = row.product_id
    else:
        pid = None
        code = (row.product_code or "").strip()
        name = (row.product_name or "").strip()
    line_total = quantize_money(qty * unit_price)
    return pid, code, name, qty, unit_price, line_total, row.notes


def _sum_items_total(items: list[InvoiceItem]) -> Decimal:
    return quantize_money(sum((i.line_total for i in items), Decimal("0")))


def _apply_items(
    db: Session,
    company_id: int,
    invoice_id: int,
    payload_items: list[InvoiceItemCreate],
) -> list[InvoiceItem]:
    built: list[InvoiceItem] = []
    for row in payload_items:
        pid, code, name, qty, unit_price, line_total, notes = _resolve_line(db, company_id, row)
        built.append(
            InvoiceItem(
                company_id=company_id,
                invoice_id=invoice_id,
                product_id=pid,
                product_code=code,
                product_name=name,
                quantity=qty,
                unit_price=unit_price,
                line_total=line_total,
                notes=notes,
            )
        )
    return built


def create_invoice(
    db: Session,
    company_id: int,
    payload: InvoiceCreate,
    *,
    created_by_user_id: int,
) -> Invoice:
    _get_client(db, company_id, payload.client_id)
    sales_order_id = payload.sales_order_id
    if sales_order_id is not None:
        order = _get_sales_order(db, company_id, sales_order_id)
        _validate_order_for_invoice(order, payload.client_id)

    if _invoice_number_taken(db, company_id, payload.invoice_number, exclude_id=None):
        raise ConflictError("Invoice number already exists for this company.")

    user = db.get(User, created_by_user_id)
    if user is None or user.company_id != company_id:
        raise NotFoundError("User not found.")

    inv = Invoice(
        company_id=company_id,
        client_id=payload.client_id,
        sales_order_id=sales_order_id,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        status=InvoiceStatus.draft,
        notes=payload.notes,
        total_amount=Decimal("0"),
        paid_amount=Decimal("0"),
        outstanding_amount=Decimal("0"),
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(inv)
    db.flush()
    for item in _apply_items(db, company_id, inv.id, payload.items):
        db.add(item)
    db.flush()
    inv.total_amount = _sum_items_total(list(inv.items))
    db.commit()
    return _get_invoice(db, company_id, inv.id)


def create_invoice_from_sales_order(
    db: Session,
    company_id: int,
    sales_order_id: int,
    payload: InvoiceFromSalesOrderCreate,
    *,
    created_by_user_id: int,
) -> Invoice:
    order = _get_sales_order(db, company_id, sales_order_id)
    _validate_order_for_invoice(order, order.client_id)

    if _invoice_number_taken(db, company_id, payload.invoice_number, exclude_id=None):
        raise ConflictError("Invoice number already exists for this company.")

    user = db.get(User, created_by_user_id)
    if user is None or user.company_id != company_id:
        raise NotFoundError("User not found.")

    stmt = (
        select(SalesOrderItem)
        .options(joinedload(SalesOrderItem.product))
        .where(
            SalesOrderItem.sales_order_id == sales_order_id,
            SalesOrderItem.company_id == company_id,
        )
    )
    so_lines = list(db.scalars(stmt).unique().all())
    if not so_lines:
        raise BusinessRuleError("Sales order has no lines to invoice.")

    inv = Invoice(
        company_id=company_id,
        client_id=order.client_id,
        sales_order_id=sales_order_id,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        status=InvoiceStatus.draft,
        notes=payload.notes,
        total_amount=Decimal("0"),
        paid_amount=Decimal("0"),
        outstanding_amount=Decimal("0"),
        is_active=True,
        created_by_user_id=created_by_user_id,
    )
    db.add(inv)
    db.flush()

    for line in so_lines:
        prod = line.product
        qty = quantize_money(line.ordered_qty)
        unit_price = quantize_money(line.unit_price)
        line_total = quantize_money(qty * unit_price)
        db.add(
            InvoiceItem(
                company_id=company_id,
                invoice_id=inv.id,
                product_id=line.product_id,
                product_code=prod.code,
                product_name=prod.name,
                quantity=qty,
                unit_price=unit_price,
                line_total=line_total,
                notes=line.notes,
            )
        )
    db.flush()
    inv.total_amount = _sum_items_total(list(inv.items))
    db.commit()
    return _get_invoice(db, company_id, inv.id)


def list_invoices(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    client_id: int | None = None,
    sales_order_id: int | None = None,
    status: InvoiceStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[Invoice]:
    stmt = (
        select(Invoice)
        .options(joinedload(Invoice.client), joinedload(Invoice.sales_order))
        .where(Invoice.company_id == company_id)
    )
    if client_id is not None:
        stmt = stmt.where(Invoice.client_id == client_id)
    if sales_order_id is not None:
        stmt = stmt.where(Invoice.sales_order_id == sales_order_id)
    if status is not None:
        stmt = stmt.where(Invoice.status == status)
    if date_from is not None:
        stmt = stmt.where(Invoice.invoice_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Invoice.invoice_date <= date_to)
    if is_active is not None:
        stmt = stmt.where(Invoice.is_active == is_active)
    if search and (t := search.strip()):
        stmt = stmt.where(Invoice.invoice_number.ilike(f"%{t}%"))
    stmt = stmt.order_by(Invoice.invoice_date.desc(), Invoice.id.desc()).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).unique().all())


def get_invoice(db: Session, company_id: int, invoice_id: int) -> Invoice:
    return _get_invoice(db, company_id, invoice_id)


def update_invoice(db: Session, company_id: int, invoice_id: int, payload: InvoiceUpdate) -> Invoice:
    inv = _get_invoice(db, company_id, invoice_id)
    if inv.status != InvoiceStatus.draft:
        raise BusinessRuleError("Only draft invoices can be updated.")
    if not inv.is_active:
        raise BusinessRuleError("Cannot update a deactivated invoice.")

    if payload.invoice_number is not None:
        if _invoice_number_taken(db, company_id, payload.invoice_number, exclude_id=inv.id):
            raise ConflictError("Invoice number already exists for this company.")
        inv.invoice_number = payload.invoice_number
    if payload.invoice_date is not None:
        inv.invoice_date = payload.invoice_date
    if payload.due_date is not None:
        inv.due_date = payload.due_date
    if payload.notes is not None:
        inv.notes = payload.notes

    if payload.items is not None:
        if len(payload.items) < 1:
            raise BusinessRuleError("Invoice must have at least one line.")
        for old in list(inv.items):
            db.delete(old)
        db.flush()
        for item in _apply_items(db, company_id, inv.id, payload.items):
            db.add(item)
        db.flush()
        inv.total_amount = _sum_items_total(list(inv.items))

    db.commit()
    return _get_invoice(db, company_id, inv.id)


def issue_invoice(db: Session, company_id: int, invoice_id: int) -> Invoice:
    inv = _get_invoice(db, company_id, invoice_id)
    if inv.status != InvoiceStatus.draft:
        raise BusinessRuleError("Only draft invoices can be issued.")
    if not inv.is_active:
        raise BusinessRuleError("Cannot issue a deactivated invoice.")
    if not inv.items:
        raise BusinessRuleError("Cannot issue an invoice without lines.")
    if inv.total_amount <= 0:
        raise BusinessRuleError("Cannot issue an invoice with zero total.")

    inv.status = InvoiceStatus.issued
    inv.paid_amount = Decimal("0")
    inv.outstanding_amount = quantize_money(inv.total_amount)
    db.commit()
    return _get_invoice(db, company_id, inv.id)


def cancel_invoice(db: Session, company_id: int, invoice_id: int) -> Invoice:
    inv = _get_invoice(db, company_id, invoice_id)
    if inv.status == InvoiceStatus.cancelled:
        raise BusinessRuleError("Invoice is already cancelled.")
    if quantize_money(inv.paid_amount) > 0:
        raise BusinessRuleError("Cannot cancel an invoice that has payment allocations; reverse allocations first.")
    inv.status = InvoiceStatus.cancelled
    inv.outstanding_amount = Decimal("0")
    db.commit()
    return _get_invoice(db, company_id, inv.id)


def deactivate_invoice(db: Session, company_id: int, invoice_id: int) -> Invoice:
    inv = _get_invoice(db, company_id, invoice_id)
    alloc_sum = db.scalar(
        select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.company_id == company_id,
            PaymentAllocation.invoice_id == invoice_id,
            PaymentAllocation.is_active.is_(True),
        )
    )
    if alloc_sum and Decimal(str(alloc_sum)) > 0:
        raise BusinessRuleError("Cannot deactivate invoice with active payment allocations.")
    inv.is_active = False
    db.commit()
    return _get_invoice(db, company_id, inv.id)


def invoice_to_summary(inv: Invoice) -> InvoiceSummaryResponse:
    so = (
        SalesOrderBriefPayment.model_validate(inv.sales_order)
        if inv.sales_order_id is not None and inv.sales_order is not None
        else None
    )
    return InvoiceSummaryResponse(
        id=inv.id,
        company_id=inv.company_id,
        client_id=inv.client_id,
        sales_order_id=inv.sales_order_id,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        due_date=inv.due_date,
        status=inv.status,
        total_amount=inv.total_amount,
        paid_amount=inv.paid_amount,
        outstanding_amount=inv.outstanding_amount,
        is_active=inv.is_active,
        created_at=inv.created_at,
        client=ClientBriefPayment.model_validate(inv.client),
        sales_order=so,
    )


def invoice_to_response(inv: Invoice) -> InvoiceResponse:
    active_allocs = [a for a in inv.payment_allocations if a.is_active]
    total_alloc = quantize_money(sum((a.allocated_amount for a in active_allocs), Decimal("0")))
    summary = AllocationsSummaryResponse(
        active_allocation_count=len(active_allocs),
        total_allocated_amount=total_alloc,
    )
    so = (
        SalesOrderBriefPayment.model_validate(inv.sales_order)
        if inv.sales_order_id is not None and inv.sales_order is not None
        else None
    )
    items_sorted = sorted(inv.items, key=lambda x: x.id)
    created_by = None
    if inv.created_by_user_id is not None and inv.created_by_user is not None:
        created_by = UserBriefInvoice.model_validate(inv.created_by_user)
    return InvoiceResponse(
        id=inv.id,
        company_id=inv.company_id,
        client_id=inv.client_id,
        sales_order_id=inv.sales_order_id,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        due_date=inv.due_date,
        status=inv.status,
        notes=inv.notes,
        total_amount=inv.total_amount,
        paid_amount=inv.paid_amount,
        outstanding_amount=inv.outstanding_amount,
        is_active=inv.is_active,
        created_by_user_id=inv.created_by_user_id,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        client=ClientBriefPayment.model_validate(inv.client),
        sales_order=so,
        items=[InvoiceItemResponse.model_validate(i) for i in items_sorted],
        allocations_summary=summary,
        created_by_user=created_by,
    )
