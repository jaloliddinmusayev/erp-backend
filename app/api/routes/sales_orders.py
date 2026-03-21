from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.sales_order import FulfillmentStatus, SalesOrderStatus
from app.models.user import User
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderFulfillmentUpdate,
    SalesOrderListResponse,
    SalesOrderResponse,
    SalesOrderUpdate,
    sales_order_to_list_response,
    sales_order_to_response,
)
from app.services import sales_order_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
def create_sales_order(
    payload: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.create_sales_order(db, current_user.company_id, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return sales_order_to_response(row)


@router.get("/", response_model=list[SalesOrderListResponse])
def list_sales_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: SalesOrderStatus | None = Query(None),
    client_id: int | None = Query(None, ge=1),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    search: str | None = Query(None, description="order_number or client name (partial, case-insensitive)."),
    is_active: bool | None = Query(None),
) -> list[SalesOrderListResponse]:
    rows = sales_order_service.list_sales_orders(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status,
        fulfillment_status=fulfillment_status,
        client_id=client_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        is_active=is_active,
    )
    return [sales_order_to_list_response(r) for r in rows]


@router.get("/{order_id}", response_model=SalesOrderResponse)
def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.get_sales_order(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return sales_order_to_response(row)


@router.put("/{order_id}", response_model=SalesOrderResponse)
def update_sales_order(
    order_id: int,
    payload: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.update_sales_order(db, current_user.company_id, order_id, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/confirm", response_model=SalesOrderResponse)
def confirm_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.confirm_sales_order(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/cancel", response_model=SalesOrderResponse)
def cancel_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.cancel_sales_order(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/deactivate", response_model=SalesOrderResponse)
def deactivate_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.deactivate_sales_order(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/send-to-wms", response_model=SalesOrderResponse)
def send_sales_order_to_wms(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.send_sales_order_to_wms(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/mark-in-progress", response_model=SalesOrderResponse)
def mark_sales_order_in_progress(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.mark_sales_order_in_progress(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/update-fulfillment", response_model=SalesOrderResponse)
def update_sales_order_fulfillment(
    order_id: int,
    payload: SalesOrderFulfillmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.update_sales_order_fulfillment(
            db, current_user.company_id, order_id, payload
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)


@router.patch("/{order_id}/complete", response_model=SalesOrderResponse)
def complete_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = sales_order_service.complete_sales_order(db, current_user.company_id, order_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)
