from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse
from app.services import warehouse_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WarehouseResponse:
    payload = payload.model_copy(update={"company_id": current_user.company_id})
    try:
        warehouse = warehouse_service.create_warehouse(db, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return WarehouseResponse.model_validate(warehouse)


@router.get("/", response_model=list[WarehouseResponse])
def list_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[WarehouseResponse]:
    try:
        rows = warehouse_service.list_warehouses_by_company(
            db,
            company_id=current_user.company_id,
            skip=skip,
            limit=limit,
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return [WarehouseResponse.model_validate(w) for w in rows]
