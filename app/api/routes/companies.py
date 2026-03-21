from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services import company_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db),
) -> CompanyResponse:
    try:
        company = company_service.create_company(db, payload)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return CompanyResponse.model_validate(company)


@router.get("/", response_model=list[CompanyResponse])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CompanyResponse]:
    companies = company_service.list_companies_for_tenant(
        db,
        company_id=current_user.company_id,
    )
    return [CompanyResponse.model_validate(c) for c in companies]
