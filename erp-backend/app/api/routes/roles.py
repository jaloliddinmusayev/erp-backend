from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.role import RoleCreate, RoleResponse
from app.services import role_service

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)) -> RoleResponse:
    try:
        role = role_service.create_role(db, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return RoleResponse.model_validate(role)


@router.get("/", response_model=list[RoleResponse])
def list_roles(
    company_id: int = Query(..., description="Tenant filter (temporary until JWT context)."),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[RoleResponse]:
    try:
        roles = role_service.list_roles_by_company(db, company_id=company_id, skip=skip, limit=limit)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return [RoleResponse.model_validate(r) for r in roles]
