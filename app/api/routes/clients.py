from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services import client_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    try:
        row = client_service.create_client(db, current_user.company_id, payload)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return ClientResponse.model_validate(row)


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, description="Filter by code, name, or phone (partial, case-insensitive)."),
    is_active: bool | None = Query(None, description="If set, only active or only inactive clients."),
) -> list[ClientResponse]:
    rows = client_service.list_clients(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
    )
    return [ClientResponse.model_validate(r) for r in rows]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    try:
        row = client_service.get_client(db, current_user.company_id, client_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return ClientResponse.model_validate(row)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    try:
        row = client_service.update_client(db, current_user.company_id, client_id, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return ClientResponse.model_validate(row)


@router.patch("/{client_id}/deactivate", response_model=ClientResponse)
def deactivate_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    try:
        row = client_service.deactivate_client(db, current_user.company_id, client_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return ClientResponse.model_validate(row)
