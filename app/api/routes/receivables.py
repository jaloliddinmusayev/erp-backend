from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.user import User
from app.schemas.receivable import (
    ClientAgingResponse,
    ClientStatementResponse,
    GlobalAgingResponse,
    InvoiceAgingDetailResponse,
)
from app.services import receivable_service, statement_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/aging", response_model=GlobalAgingResponse)
def get_global_aging(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    as_of_date: date | None = Query(None, description="Aging anchor date (default: today, UTC-naive calendar)."),
) -> GlobalAgingResponse:
    return receivable_service.get_global_aging_summary(db, current_user.company_id, as_of_date=as_of_date)


@router.get("/aging/invoices", response_model=list[InvoiceAgingDetailResponse])
def list_aging_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_id: int | None = Query(None, ge=1),
    as_of_date: date | None = Query(None),
) -> list[InvoiceAgingDetailResponse]:
    try:
        return receivable_service.list_aging_invoices(
            db, current_user.company_id, client_id=client_id, as_of_date=as_of_date
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e


@router.get("/aging/client/{client_id}", response_model=ClientAgingResponse)
def get_client_aging(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    as_of_date: date | None = Query(None),
    include_invoices: bool = Query(False, description="Include open invoice detail rows in the response."),
) -> ClientAgingResponse:
    try:
        return receivable_service.get_client_aging_summary(
            db,
            current_user.company_id,
            client_id,
            as_of_date=as_of_date,
            include_invoices=include_invoices,
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e


@router.get("/statements/client/{client_id}", response_model=ClientStatementResponse)
def get_client_statement(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
) -> ClientStatementResponse:
    try:
        return statement_service.get_client_statement(
            db, current_user.company_id, client_id, date_from=date_from, date_to=date_to
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
