from datetime import datetime

from pydantic import BaseModel, Field

from app.models.integration_job import IntegrationJobStatus


class IntegrationJobResponse(BaseModel):
    id: int
    company_id: int
    entity_type: str
    entity_id: int
    event_type: str
    payload_json: str
    status: IntegrationJobStatus
    attempt_count: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class IntegrationJobMarkSent(BaseModel):
    wms_order_id: str = Field(..., min_length=1, max_length=128)


class IntegrationJobMarkFailed(BaseModel):
    error: str = Field(..., min_length=1, max_length=4000)


def integration_job_to_response(job) -> IntegrationJobResponse:
    return IntegrationJobResponse(
        id=job.id,
        company_id=job.company_id,
        entity_type=job.entity_type,
        entity_id=job.entity_id,
        event_type=job.event_type,
        payload_json=job.payload_json,
        status=job.status,
        attempt_count=job.attempt_count,
        last_error=job.last_error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
