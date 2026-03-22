from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.integration_job import IntegrationJobStatus
from app.models.sales_order import FulfillmentStatus, IntegrationStatus, SalesOrderStatus


class ClientBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class BranchBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class ProductBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class SalesOrderItemCreate(BaseModel):
    product_id: int
    ordered_qty: Decimal = Field(..., gt=0, max_digits=18, decimal_places=4)
    unit_price: Decimal = Field(..., ge=0, max_digits=18, decimal_places=4)
    notes: str | None = None


class SalesOrderItemUpdate(BaseModel):
    """Same shape as create; used when replacing lines on order update."""

    product_id: int
    ordered_qty: Decimal = Field(..., gt=0, max_digits=18, decimal_places=4)
    unit_price: Decimal = Field(..., ge=0, max_digits=18, decimal_places=4)
    notes: str | None = None


class SalesOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    sales_order_id: int
    product_id: int
    ordered_qty: Decimal
    fulfilled_qty: Decimal
    remaining_qty: Decimal
    unit_price: Decimal
    line_total: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    product: ProductBrief


class SalesOrderCreate(BaseModel):
    client_id: int
    branch_id: int | None = None
    order_number: str = Field(..., min_length=1, max_length=64)
    order_date: date
    notes: str | None = None
    items: list[SalesOrderItemCreate] = Field(..., min_length=1)

    @field_validator("order_number")
    @classmethod
    def strip_order_number(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("order_number cannot be empty")
        return s


class SalesOrderUpdate(BaseModel):
    client_id: int
    branch_id: int | None = None
    order_number: str = Field(..., min_length=1, max_length=64)
    order_date: date
    notes: str | None = None
    items: list[SalesOrderItemUpdate] = Field(..., min_length=1)

    @field_validator("order_number")
    @classmethod
    def strip_order_number(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("order_number cannot be empty")
        return s


class FulfillmentLineUpdate(BaseModel):
    item_id: int = Field(..., ge=1)
    fulfilled_qty: Decimal = Field(..., ge=0, max_digits=18, decimal_places=4)


class SalesOrderFulfillmentUpdate(BaseModel):
    lines: list[FulfillmentLineUpdate] = Field(..., min_length=1)


class SalesOrderResponse(BaseModel):
    id: int
    company_id: int
    client_id: int
    branch_id: int | None
    order_number: str
    order_date: date
    status: SalesOrderStatus
    fulfillment_status: FulfillmentStatus
    fulfilled_at: datetime | None
    is_sent_to_wms: bool
    wms_order_id: str | None
    integration_status: IntegrationStatus
    sent_to_wms_at: datetime | None
    last_sync_error: str | None
    notes: str | None
    total_amount: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    client: ClientBrief
    branch: BranchBrief | None
    items: list[SalesOrderItemResponse]


class SalesOrderListResponse(BaseModel):
    id: int
    company_id: int
    client_id: int
    branch_id: int | None
    order_number: str
    order_date: date
    status: SalesOrderStatus
    fulfillment_status: FulfillmentStatus
    fulfilled_at: datetime | None
    is_sent_to_wms: bool
    wms_order_id: str | None
    integration_status: IntegrationStatus
    sent_to_wms_at: datetime | None
    last_sync_error: str | None
    notes: str | None
    total_amount: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    client: ClientBrief
    branch: BranchBrief | None


_ITEM_QUANT = Decimal("0.0001")


def _item_remaining(it) -> Decimal:
    o = it.ordered_qty.quantize(_ITEM_QUANT, rounding=ROUND_HALF_UP)
    f = it.fulfilled_qty.quantize(_ITEM_QUANT, rounding=ROUND_HALF_UP)
    r = (o - f).quantize(_ITEM_QUANT, rounding=ROUND_HALF_UP)
    return r if r > 0 else Decimal("0")


def sales_order_to_list_response(order) -> SalesOrderListResponse:
    return SalesOrderListResponse(
        id=order.id,
        company_id=order.company_id,
        client_id=order.client_id,
        branch_id=order.branch_id,
        order_number=order.order_number,
        order_date=order.order_date,
        status=order.status,
        fulfillment_status=order.fulfillment_status,
        fulfilled_at=order.fulfilled_at,
        is_sent_to_wms=order.is_sent_to_wms,
        wms_order_id=order.wms_order_id,
        integration_status=order.integration_status,
        sent_to_wms_at=order.sent_to_wms_at,
        last_sync_error=order.last_sync_error,
        notes=order.notes,
        total_amount=order.total_amount,
        is_active=order.is_active,
        created_at=order.created_at,
        updated_at=order.updated_at,
        client=ClientBrief.model_validate(order.client),
        branch=BranchBrief.model_validate(order.branch) if order.branch_id is not None else None,
    )


def sales_order_to_response(order) -> SalesOrderResponse:
    items_out: list[SalesOrderItemResponse] = []
    for it in sorted(order.items, key=lambda x: x.id):
        items_out.append(
            SalesOrderItemResponse(
                id=it.id,
                company_id=it.company_id,
                sales_order_id=it.sales_order_id,
                product_id=it.product_id,
                ordered_qty=it.ordered_qty,
                fulfilled_qty=it.fulfilled_qty,
                remaining_qty=_item_remaining(it),
                unit_price=it.unit_price,
                line_total=it.line_total,
                notes=it.notes,
                created_at=it.created_at,
                updated_at=it.updated_at,
                product=ProductBrief.model_validate(it.product),
            )
        )
    return SalesOrderResponse(
        id=order.id,
        company_id=order.company_id,
        client_id=order.client_id,
        branch_id=order.branch_id,
        order_number=order.order_number,
        order_date=order.order_date,
        status=order.status,
        fulfillment_status=order.fulfillment_status,
        fulfilled_at=order.fulfilled_at,
        is_sent_to_wms=order.is_sent_to_wms,
        wms_order_id=order.wms_order_id,
        integration_status=order.integration_status,
        sent_to_wms_at=order.sent_to_wms_at,
        last_sync_error=order.last_sync_error,
        notes=order.notes,
        total_amount=order.total_amount,
        is_active=order.is_active,
        created_at=order.created_at,
        updated_at=order.updated_at,
        client=ClientBrief.model_validate(order.client),
        branch=BranchBrief.model_validate(order.branch) if order.branch_id is not None else None,
        items=items_out,
    )


class EnqueueWmsResponse(BaseModel):
    order: SalesOrderResponse
    integration_job_id: int
    job_status: IntegrationJobStatus
