from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.user import User
from app.schemas.payment_allocation import PaymentAllocationCreate, PaymentAllocationResponse
from app.services import payment_allocation_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=PaymentAllocationResponse, status_code=status.HTTP_201_CREATED)
def create_payment_allocation(
    payload: PaymentAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentAllocationResponse:
    try:
        row = payment_allocation_service.create_payment_allocation(
            db, current_user.company_id, payload, created_by_user_id=current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return payment_allocation_service.payment_allocation_to_response(row)


@router.get("/", response_model=list[PaymentAllocationResponse])
def list_payment_allocations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    payment_id: int | None = Query(None, ge=1),
    invoice_id: int | None = Query(None, ge=1),
    is_active: bool | None = Query(None),
) -> list[PaymentAllocationResponse]:
    rows = payment_allocation_service.list_payment_allocations(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        payment_id=payment_id,
        invoice_id=invoice_id,
        is_active=is_active,
    )
    return [payment_allocation_service.payment_allocation_to_response(r) for r in rows]


@router.get("/{allocation_id}", response_model=PaymentAllocationResponse)
def get_payment_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentAllocationResponse:
    try:
        row = payment_allocation_service.get_payment_allocation(db, current_user.company_id, allocation_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return payment_allocation_service.payment_allocation_to_response(row)


@router.patch("/{allocation_id}/deactivate", response_model=PaymentAllocationResponse)
def deactivate_payment_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentAllocationResponse:
    try:
        row = payment_allocation_service.deactivate_payment_allocation(
            db, current_user.company_id, allocation_id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return payment_allocation_service.payment_allocation_to_response(row)
