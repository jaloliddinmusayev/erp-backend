from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.role import RoleCreate, RoleResponse
from app.services import role_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoleResponse:
    payload = payload.model_copy(update={"company_id": current_user.company_id})
    try:
        role = role_service.create_role(db, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return RoleResponse.model_validate(role)


@router.get("/", response_model=list[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[RoleResponse]:
    try:
        roles = role_service.list_roles_by_company(
            db,
            company_id=current_user.company_id,
            skip=skip,
            limit=limit,
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return [RoleResponse.model_validate(r) for r in roles]
