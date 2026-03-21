from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.unit import UnitCreate, UnitResponse, UnitUpdate
from app.services import unit_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    payload: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    try:
        row = unit_service.create_unit(db, current_user.company_id, payload)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return UnitResponse.model_validate(row)


@router.get("/", response_model=list[UnitResponse])
def list_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[UnitResponse]:
    rows = unit_service.list_units(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return [UnitResponse.model_validate(r) for r in rows]


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    try:
        row = unit_service.get_unit(db, current_user.company_id, unit_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return UnitResponse.model_validate(row)


@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    try:
        row = unit_service.update_unit(db, current_user.company_id, unit_id, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return UnitResponse.model_validate(row)


@router.patch("/{unit_id}/deactivate", response_model=UnitResponse)
def deactivate_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    try:
        row = unit_service.deactivate_unit(db, current_user.company_id, unit_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return UnitResponse.model_validate(row)
