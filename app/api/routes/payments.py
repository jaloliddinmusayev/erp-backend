from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.payment import PaymentMethod
from app.models.user import User
from app.schemas.payment import (
    ClientReceivableResponse,
    PaymentCreate,
    PaymentResponse,
    SalesOrderPaymentSummaryResponse,
    payment_to_response,
)
from app.schemas.payment_allocation import PaymentUnallocatedResponse
from app.services import payment_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    try:
        row = payment_service.create_payment(
            db, current_user.company_id, payload, created_by_user_id=current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return payment_to_response(row)


@router.get("/", response_model=list[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    client_id: int | None = Query(None, ge=1),
    sales_order_id: int | None = Query(None, ge=1),
    payment_method: PaymentMethod | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    search: str | None = Query(None, description="reference_number or notes (partial match)."),
    is_active: bool | None = Query(None),
) -> list[PaymentResponse]:
    rows = payment_service.list_payments(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        client_id=client_id,
        sales_order_id=sales_order_id,
        payment_method=payment_method,
        date_from=date_from,
        date_to=date_to,
        search=search,
        is_active=is_active,
    )
    return [payment_to_response(r) for r in rows]


@router.get("/client-summary/{client_id}", response_model=ClientReceivableResponse)
def get_client_receivable_summary(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientReceivableResponse:
    try:
        return payment_service.get_client_receivable_summary(db, current_user.company_id, client_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e


@router.get("/sales-order-summary/{sales_order_id}", response_model=SalesOrderPaymentSummaryResponse)
def get_sales_order_payment_summary(
    sales_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderPaymentSummaryResponse:
    try:
        return payment_service.get_sales_order_payment_summary(
            db, current_user.company_id, sales_order_id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e


@router.get("/{payment_id}/unallocated-amount", response_model=PaymentUnallocatedResponse)
def get_payment_unallocated_amount(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentUnallocatedResponse:
    try:
        return payment_service.get_payment_unallocated_breakdown(db, current_user.company_id, payment_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    try:
        row = payment_service.get_payment(db, current_user.company_id, payment_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return payment_to_response(row)


@router.patch("/{payment_id}/deactivate", response_model=PaymentResponse)
def deactivate_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    try:
        row = payment_service.deactivate_payment(db, current_user.company_id, payment_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return payment_to_response(row)
