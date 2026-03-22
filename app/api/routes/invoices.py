from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.invoice import InvoiceStatus
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceFromSalesOrderCreate,
    InvoiceResponse,
    InvoiceSummaryResponse,
    InvoiceUpdate,
)
from app.services import invoice_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.create_invoice(
            db, current_user.company_id, payload, created_by_user_id=current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.post(
    "/from-sales-order/{sales_order_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_from_sales_order(
    sales_order_id: int,
    payload: InvoiceFromSalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.create_invoice_from_sales_order(
            db,
            current_user.company_id,
            sales_order_id,
            payload,
            created_by_user_id=current_user.id,
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.get("/", response_model=list[InvoiceSummaryResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    client_id: int | None = Query(None, ge=1),
    sales_order_id: int | None = Query(None, ge=1),
    status: InvoiceStatus | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    search: str | None = Query(None, description="invoice_number partial match."),
    is_active: bool | None = Query(None),
) -> list[InvoiceSummaryResponse]:
    rows = invoice_service.list_invoices(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        client_id=client_id,
        sales_order_id=sales_order_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        is_active=is_active,
    )
    return [invoice_service.invoice_to_summary(r) for r in rows]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.get_invoice(db, current_user.company_id, invoice_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.update_invoice(db, current_user.company_id, invoice_id, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.patch("/{invoice_id}/issue", response_model=InvoiceResponse)
def issue_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.issue_invoice(db, current_user.company_id, invoice_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.patch("/{invoice_id}/cancel", response_model=InvoiceResponse)
def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.cancel_invoice(db, current_user.company_id, invoice_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)


@router.patch("/{invoice_id}/deactivate", response_model=InvoiceResponse)
def deactivate_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceResponse:
    try:
        row = invoice_service.deactivate_invoice(db, current_user.company_id, invoice_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return invoice_service.invoice_to_response(row)
