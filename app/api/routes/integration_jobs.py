from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.integration_job import IntegrationJobStatus
from app.models.user import User
from app.schemas.integration_job import (
    IntegrationJobMarkFailed,
    IntegrationJobMarkSent,
    IntegrationJobResponse,
    integration_job_to_response,
)
from app.services import integration_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[IntegrationJobResponse])
def list_integration_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: IntegrationJobStatus | None = Query(None),
    entity_type: str | None = Query(None),
    event_type: str | None = Query(None),
) -> list[IntegrationJobResponse]:
    rows = integration_service.list_integration_jobs(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        status=status,
        entity_type=entity_type,
        event_type=event_type,
    )
    return [integration_job_to_response(r) for r in rows]


@router.get("/{job_id}", response_model=IntegrationJobResponse)
def get_integration_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntegrationJobResponse:
    try:
        row = integration_service.get_integration_job(db, current_user.company_id, job_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return integration_job_to_response(row)


@router.patch("/{job_id}/mark-sent", response_model=IntegrationJobResponse)
def mark_integration_job_sent(
    job_id: int,
    payload: IntegrationJobMarkSent,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> IntegrationJobResponse:
    try:
        row = integration_service.mark_integration_job_sent(
            db, current_user.company_id, job_id, payload.wms_order_id
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return integration_job_to_response(row)


@router.patch("/{job_id}/mark-failed", response_model=IntegrationJobResponse)
def mark_integration_job_failed(
    job_id: int,
    payload: IntegrationJobMarkFailed,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> IntegrationJobResponse:
    try:
        row = integration_service.mark_integration_job_failed(
            db, current_user.company_id, job_id, payload.error
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return integration_job_to_response(row)
