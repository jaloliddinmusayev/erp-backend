from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.exceptions import ConflictError
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services import company_service

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> CompanyResponse:
    try:
        company = company_service.create_company(db, payload)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return CompanyResponse.model_validate(company)


@router.get("/", response_model=list[CompanyResponse])
def list_companies(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[CompanyResponse]:
    companies = company_service.list_companies(db, skip=skip, limit=limit)
    return [CompanyResponse.model_validate(c) for c in companies]
