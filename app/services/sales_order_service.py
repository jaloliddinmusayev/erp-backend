from collections.abc import Sequence
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.branch import Branch
from app.models.client import Client
from app.models.product import Product
from app.models.sales_order import (
    FulfillmentStatus,
    IntegrationStatus,
    SalesOrder,
    SalesOrderItem,
    SalesOrderStatus,
)
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderFulfillmentUpdate,
    SalesOrderItemCreate,
    SalesOrderItemUpdate,
    SalesOrderUpdate,
)

MONEY_QUANT = Decimal("0.0001")


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _line_total(ordered_qty: Decimal, unit_price: Decimal) -> Decimal:
    return _quantize_money(ordered_qty * unit_price)


def _recalculate_fulfillment_status(order: SalesOrder, items: list[SalesOrderItem] | None = None) -> None:
    seq = items if items is not None else list(order.items)
    if not seq:
        order.fulfillment_status = FulfillmentStatus.pending
        return
    all_zero = all(_quantize_money(it.fulfilled_qty) == Decimal("0") for it in seq)
    all_full = all(
        _quantize_money(it.fulfilled_qty) == _quantize_money(it.ordered_qty) for it in seq
    )
    if all_zero:
        order.fulfillment_status = FulfillmentStatus.pending
    elif all_full:
        order.fulfillment_status = FulfillmentStatus.fulfilled
    else:
        order.fulfillment_status = FulfillmentStatus.partial


def apply_fulfillment_updates_to_order(order: SalesOrder, payload: SalesOrderFulfillmentUpdate) -> None:
    """Apply line fulfilled_qty; recalculates header fulfillment_status. No commit."""
    by_id = {it.id: it for it in order.items}
    seen: set[int] = set()
    for line in payload.lines:
        if line.item_id in seen:
            raise BusinessRuleError("Duplicate item_id in fulfillment payload.")
        seen.add(line.item_id)
        item = by_id.get(line.item_id)
        if item is None:
            raise NotFoundError("Sales order line not found.")
        fq = _quantize_money(line.fulfilled_qty)
        oq = _quantize_money(item.ordered_qty)
        if fq > oq:
            raise BusinessRuleError("Fulfilled quantity cannot exceed ordered quantity.")
        item.fulfilled_qty = fq
    _recalculate_fulfillment_status(order)


def _assert_all_lines_fully_fulfilled(order: SalesOrder) -> None:
    for it in order.items:
        if _quantize_money(it.fulfilled_qty) != _quantize_money(it.ordered_qty):
            raise BusinessRuleError("Cannot complete while some lines have remaining quantity.")


def _ensure_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def _ensure_branch(db: Session, company_id: int, branch_id: int) -> Branch:
    row = db.get(Branch, branch_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Branch not found.")
    return row


def _ensure_product(db: Session, company_id: int, product_id: int) -> Product:
    row = db.get(Product, product_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Product not found.")
    return row


def _get_sales_order_for_list(db: Session, company_id: int, order_id: int) -> SalesOrder:
    stmt = (
        select(SalesOrder)
        .where(SalesOrder.id == order_id, SalesOrder.company_id == company_id)
        .options(selectinload(SalesOrder.client), selectinload(SalesOrder.branch))
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Sales order not found.")
    return row


def _get_sales_order_detail(db: Session, company_id: int, order_id: int) -> SalesOrder:
    stmt = (
        select(SalesOrder)
        .where(SalesOrder.id == order_id, SalesOrder.company_id == company_id)
        .options(
            selectinload(SalesOrder.client),
            selectinload(SalesOrder.branch),
            selectinload(SalesOrder.items).selectinload(SalesOrderItem.product),
        )
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise NotFoundError("Sales order not found.")
    return row


def _assert_mutable_draft(order: SalesOrder) -> None:
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status != SalesOrderStatus.draft:
        raise BusinessRuleError(
            "Only draft sales orders can be edited (not after confirm / WMS / fulfillment)."
        )


def _replace_line_items(
    db: Session,
    order: SalesOrder,
    company_id: int,
    lines: Sequence[SalesOrderItemCreate | SalesOrderItemUpdate],
) -> Decimal:
    db.execute(delete(SalesOrderItem).where(SalesOrderItem.sales_order_id == order.id))
    db.flush()
    running = Decimal("0")
    for line in lines:
        _ensure_product(db, company_id, line.product_id)
        qty = _quantize_money(line.ordered_qty)
        price = _quantize_money(line.unit_price)
        lt = _line_total(qty, price)
        running += lt
        db.add(
            SalesOrderItem(
                company_id=company_id,
                sales_order_id=order.id,
                product_id=line.product_id,
                ordered_qty=qty,
                fulfilled_qty=Decimal("0"),
                unit_price=price,
                line_total=lt,
                notes=line.notes,
            )
        )
    db.flush()
    new_items = list(
        db.scalars(select(SalesOrderItem).where(SalesOrderItem.sales_order_id == order.id)).all()
    )
    _recalculate_fulfillment_status(order, new_items)
    return _quantize_money(running)


def create_sales_order(db: Session, company_id: int, payload: SalesOrderCreate) -> SalesOrder:
    _ensure_client(db, company_id, payload.client_id)
    if payload.branch_id is not None:
        _ensure_branch(db, company_id, payload.branch_id)

    order = SalesOrder(
        company_id=company_id,
        client_id=payload.client_id,
        branch_id=payload.branch_id,
        order_number=payload.order_number,
        order_date=payload.order_date,
        status=SalesOrderStatus.draft,
        fulfillment_status=FulfillmentStatus.pending,
        fulfilled_at=None,
        is_sent_to_wms=False,
        wms_order_id=None,
        integration_status=IntegrationStatus.not_sent,
        sent_to_wms_at=None,
        last_sync_error=None,
        notes=payload.notes,
        total_amount=Decimal("0"),
        is_active=True,
    )
    db.add(order)
    db.flush()
    try:
        order.total_amount = _replace_line_items(db, order, company_id, payload.items)
        db.commit()
    except NotFoundError:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise ConflictError("Order number already exists for this company.") from None
    return _get_sales_order_detail(db, company_id, order.id)


def list_sales_orders(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    status: SalesOrderStatus | None = None,
    fulfillment_status: FulfillmentStatus | None = None,
    integration_status: IntegrationStatus | None = None,
    client_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[SalesOrder]:
    stmt = (
        select(SalesOrder)
        .where(SalesOrder.company_id == company_id)
        .options(selectinload(SalesOrder.client), selectinload(SalesOrder.branch))
    )
    if status is not None:
        stmt = stmt.where(SalesOrder.status == status)
    if fulfillment_status is not None:
        stmt = stmt.where(SalesOrder.fulfillment_status == fulfillment_status)
    if integration_status is not None:
        stmt = stmt.where(SalesOrder.integration_status == integration_status)
    if client_id is not None:
        stmt = stmt.where(SalesOrder.client_id == client_id)
    if date_from is not None:
        stmt = stmt.where(SalesOrder.order_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(SalesOrder.order_date <= date_to)
    if is_active is not None:
        stmt = stmt.where(SalesOrder.is_active == is_active)
    if search and (t := search.strip()):
        term = f"%{t}%"
        stmt = (
            stmt.join(Client, Client.id == SalesOrder.client_id)
            .where(or_(SalesOrder.order_number.ilike(term), Client.name.ilike(term)))
            .distinct()
        )
    stmt = stmt.order_by(SalesOrder.order_date.desc(), SalesOrder.id.desc()).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).unique().all())


def get_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    return _get_sales_order_detail(db, company_id, order_id)


def update_sales_order(db: Session, company_id: int, order_id: int, payload: SalesOrderUpdate) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    _assert_mutable_draft(order)

    _ensure_client(db, company_id, payload.client_id)
    if payload.branch_id is not None:
        _ensure_branch(db, company_id, payload.branch_id)

    order.client_id = payload.client_id
    order.branch_id = payload.branch_id
    order.order_number = payload.order_number
    order.order_date = payload.order_date
    order.notes = payload.notes

    try:
        order.total_amount = _replace_line_items(db, order, company_id, payload.items)
        db.commit()
    except NotFoundError:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise ConflictError("Order number already exists for this company.") from None
    return _get_sales_order_detail(db, company_id, order_id)


def confirm_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot confirm a cancelled order.")
    if order.status != SalesOrderStatus.draft:
        raise BusinessRuleError("Only draft sales orders can be confirmed.")
    order.status = SalesOrderStatus.confirmed
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)


def cancel_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise ConflictError("Order is already cancelled.")
    if order.status == SalesOrderStatus.completed:
        raise BusinessRuleError("Cannot cancel a completed order.")
    order.status = SalesOrderStatus.cancelled
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)


def send_sales_order_to_wms(db: Session, company_id: int, order_id: int) -> SalesOrder:
    """Legacy path name: enqueues an outbound WMS job (order stays confirmed until job is marked sent)."""
    from app.services import integration_service

    order, _ = integration_service.enqueue_sales_order_for_wms(db, company_id, order_id)
    return order


def mark_sales_order_in_progress(db: Session, company_id: int, order_id: int) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot change a cancelled order.")
    if order.status != SalesOrderStatus.sent_to_wms:
        raise BusinessRuleError("Order must be in sent_to_wms state before marking in progress.")
    order.status = SalesOrderStatus.in_progress
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)


def update_sales_order_fulfillment(
    db: Session,
    company_id: int,
    order_id: int,
    payload: SalesOrderFulfillmentUpdate,
) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot update fulfillment on a cancelled order.")
    if order.status != SalesOrderStatus.in_progress:
        raise BusinessRuleError("Fulfillment can only be updated while the order is in progress.")

    apply_fulfillment_updates_to_order(order, payload)
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)


def complete_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    order = _get_sales_order_detail(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot complete a cancelled order.")
    if order.status == SalesOrderStatus.completed:
        raise BusinessRuleError("Order is already completed.")
    if order.status != SalesOrderStatus.in_progress:
        raise BusinessRuleError("Only in-progress orders can be completed.")
    _assert_all_lines_fully_fulfilled(order)
    order.status = SalesOrderStatus.completed
    order.fulfilled_at = datetime.now(UTC)
    _recalculate_fulfillment_status(order)
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)


def deactivate_sales_order(db: Session, company_id: int, order_id: int) -> SalesOrder:
    order = _get_sales_order_for_list(db, company_id, order_id)
    order.is_active = False
    db.commit()
    return _get_sales_order_detail(db, company_id, order_id)
