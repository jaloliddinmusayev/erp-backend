"""Outbound integration jobs, WMS callbacks, and worker finalization helpers."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.integration_job import (
    ENTITY_TYPE_SALES_ORDER,
    EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER,
    IntegrationJob,
    IntegrationJobStatus,
)
from app.models.sales_order import IntegrationStatus, SalesOrder, SalesOrderStatus
from app.schemas.sales_order import SalesOrderFulfillmentUpdate
from app.services import sales_order_service

logger = logging.getLogger(__name__)


def _set_order_wms_sent_state(order: SalesOrder, wms_order_id: str) -> None:
    wms_id = wms_order_id.strip()
    if not wms_id:
        raise BusinessRuleError("wms_order_id is required.")
    order.wms_order_id = wms_id
    order.integration_status = IntegrationStatus.sent
    order.sent_to_wms_at = datetime.now(UTC)
    order.last_sync_error = None
    order.status = SalesOrderStatus.sent_to_wms
    order.is_sent_to_wms = True


def _set_order_wms_failed_state(order: SalesOrder, error_message: str) -> None:
    msg = (error_message or "").strip() or "Unknown error"
    order.integration_status = IntegrationStatus.failed
    order.last_sync_error = msg


def _active_outbound_job_exists(db: Session, company_id: int, entity_id: int) -> bool:
    stmt = (
        select(IntegrationJob.id)
        .where(
            IntegrationJob.company_id == company_id,
            IntegrationJob.entity_type == ENTITY_TYPE_SALES_ORDER,
            IntegrationJob.entity_id == entity_id,
            IntegrationJob.status.in_(
                (IntegrationJobStatus.pending, IntegrationJobStatus.processing)
            ),
        )
        .limit(1)
    )
    return db.scalars(stmt).first() is not None


def _build_sales_order_wms_payload(order: SalesOrder) -> dict[str, Any]:
    lines: list[dict[str, Any]] = []
    for it in sorted(order.items, key=lambda x: x.id):
        lines.append(
            {
                "item_id": it.id,
                "product_id": it.product_id,
                "ordered_qty": str(it.ordered_qty),
                "unit_price": str(it.unit_price),
            }
        )
    return {
        "entity_type": ENTITY_TYPE_SALES_ORDER,
        "sales_order_id": order.id,
        "company_id": order.company_id,
        "order_number": order.order_number,
        "order_date": order.order_date.isoformat(),
        "client_id": order.client_id,
        "branch_id": order.branch_id,
        "total_amount": str(order.total_amount),
        "lines": lines,
    }


def _get_job(db: Session, company_id: int, job_id: int) -> IntegrationJob:
    row = db.get(IntegrationJob, job_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Integration job not found.")
    return row


def enqueue_sales_order_for_wms(db: Session, company_id: int, order_id: int) -> tuple[SalesOrder, IntegrationJob]:
    order = sales_order_service.get_sales_order(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot enqueue a cancelled order for WMS.")
    if order.status != SalesOrderStatus.confirmed:
        raise BusinessRuleError("Only confirmed sales orders can be enqueued for WMS.")
    if order.integration_status in (
        IntegrationStatus.pending,
        IntegrationStatus.sent,
        IntegrationStatus.acknowledged,
    ):
        raise ConflictError("Order is already queued or synced with WMS; cannot enqueue again.")
    if _active_outbound_job_exists(db, company_id, order_id):
        raise ConflictError("An outbound WMS job is already pending for this order.")

    payload = _build_sales_order_wms_payload(order)
    job = IntegrationJob(
        company_id=company_id,
        entity_type=ENTITY_TYPE_SALES_ORDER,
        entity_id=order.id,
        event_type=EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER,
        payload_json=json.dumps(payload, default=str),
        status=IntegrationJobStatus.pending,
        attempt_count=0,
        last_error=None,
    )
    order.integration_status = IntegrationStatus.pending
    order.last_sync_error = None
    db.add(job)
    db.commit()
    db.refresh(job)
    return sales_order_service.get_sales_order(db, company_id, order_id), job


def mark_sales_order_sent(db: Session, company_id: int, order_id: int, wms_order_id: str) -> SalesOrder:
    order = sales_order_service.get_sales_order(db, company_id, order_id)
    _set_order_wms_sent_state(order, wms_order_id)
    db.commit()
    return sales_order_service.get_sales_order(db, company_id, order_id)


def mark_sales_order_failed(db: Session, company_id: int, order_id: int, error_message: str) -> SalesOrder:
    order = sales_order_service.get_sales_order(db, company_id, order_id)
    _set_order_wms_failed_state(order, error_message)
    db.commit()
    return sales_order_service.get_sales_order(db, company_id, order_id)


def mark_integration_job_sent(
    db: Session,
    company_id: int,
    job_id: int,
    wms_order_id: str,
) -> IntegrationJob:
    job = _get_job(db, company_id, job_id)
    if job.status not in (IntegrationJobStatus.pending, IntegrationJobStatus.processing):
        raise BusinessRuleError("Job cannot be marked sent from its current status.")
    if job.entity_type != ENTITY_TYPE_SALES_ORDER:
        raise BusinessRuleError("Unsupported entity type for this operation.")

    order = sales_order_service.get_sales_order(db, company_id, job.entity_id)
    _set_order_wms_sent_state(order, wms_order_id)
    job.status = IntegrationJobStatus.sent
    job.attempt_count = job.attempt_count + 1
    job.last_error = None
    db.commit()
    db.refresh(job)
    return job


def mark_integration_job_failed(db: Session, company_id: int, job_id: int, error_message: str) -> IntegrationJob:
    job = _get_job(db, company_id, job_id)
    if job.status not in (IntegrationJobStatus.pending, IntegrationJobStatus.processing):
        raise BusinessRuleError("Job cannot be marked failed from its current status.")
    if job.entity_type != ENTITY_TYPE_SALES_ORDER:
        raise BusinessRuleError("Unsupported entity type for this operation.")

    msg = (error_message or "").strip() or "Unknown error"
    order = sales_order_service.get_sales_order(db, company_id, job.entity_id)
    _set_order_wms_failed_state(order, msg)
    job.status = IntegrationJobStatus.failed
    job.attempt_count = job.attempt_count + 1
    job.last_error = msg
    db.commit()
    db.refresh(job)
    return job


def apply_wms_fulfillment_update(
    db: Session,
    company_id: int,
    order_id: int,
    payload: SalesOrderFulfillmentUpdate,
) -> SalesOrder:
    order = sales_order_service.get_sales_order(db, company_id, order_id)
    if not order.is_active:
        raise BusinessRuleError("Sales order is inactive.")
    if order.status == SalesOrderStatus.cancelled:
        raise BusinessRuleError("Cannot update fulfillment on a cancelled order.")
    if order.status not in (SalesOrderStatus.sent_to_wms, SalesOrderStatus.in_progress):
        raise BusinessRuleError("WMS fulfillment updates are only allowed after the order is sent to WMS.")
    if order.integration_status not in (IntegrationStatus.sent, IntegrationStatus.acknowledged):
        raise BusinessRuleError("Order must be in WMS sent or acknowledged integration state.")

    sales_order_service.apply_fulfillment_updates_to_order(order, payload)
    if order.status == SalesOrderStatus.sent_to_wms:
        order.status = SalesOrderStatus.in_progress
    if order.integration_status == IntegrationStatus.sent:
        order.integration_status = IntegrationStatus.acknowledged
    db.commit()
    return sales_order_service.get_sales_order(db, company_id, order_id)


def list_integration_jobs(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    status: IntegrationJobStatus | None = None,
    entity_type: str | None = None,
    event_type: str | None = None,
) -> list[IntegrationJob]:
    stmt = select(IntegrationJob).where(IntegrationJob.company_id == company_id)
    if status is not None:
        stmt = stmt.where(IntegrationJob.status == status)
    if entity_type is not None and (et := entity_type.strip()):
        stmt = stmt.where(IntegrationJob.entity_type == et)
    if event_type is not None and (ev := event_type.strip()):
        stmt = stmt.where(IntegrationJob.event_type == ev)
    stmt = stmt.order_by(IntegrationJob.id.desc()).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).all())


def get_integration_job(db: Session, company_id: int, job_id: int) -> IntegrationJob:
    return _get_job(db, company_id, job_id)


def reclaim_stale_processing_jobs(db: Session, *, stale_after_seconds: int) -> int:
    """Reset jobs stuck in `processing` (e.g. worker crash) back to `pending`."""
    if stale_after_seconds <= 0:
        return 0
    cutoff = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
    stmt = (
        update(IntegrationJob)
        .where(
            IntegrationJob.status == IntegrationJobStatus.processing,
            IntegrationJob.updated_at < cutoff,
        )
        .values(
            status=IntegrationJobStatus.pending,
            last_error="Stale processing lease expired; returned to pending for retry",
        )
    )
    result = db.execute(stmt)
    db.commit()
    return int(result.rowcount or 0)


def claim_pending_jobs_for_worker(
    db: Session,
    *,
    limit: int,
    max_attempts: int,
) -> list[int]:
    """
    Lock a batch of pending jobs (SKIP LOCKED), set `processing`, commit.
    Only jobs with attempt_count < max_attempts are eligible.
    """
    lim = max(1, min(limit, 100))
    stmt = (
        select(IntegrationJob)
        .where(
            IntegrationJob.status == IntegrationJobStatus.pending,
            IntegrationJob.attempt_count < max_attempts,
        )
        .order_by(IntegrationJob.id)
        .limit(lim)
        .with_for_update(skip_locked=True)
    )
    rows = list(db.scalars(stmt).all())
    for job in rows:
        job.status = IntegrationJobStatus.processing
    ids = [j.id for j in rows]
    db.commit()
    return ids


def finalize_worker_job_success(db: Session, job_id: int, wms_order_id: str) -> None:
    job = db.get(IntegrationJob, job_id)
    if job is None or job.status != IntegrationJobStatus.processing:
        logger.warning("finalize_worker_job_success skipped job_id=%s state=%s", job_id, getattr(job, "status", None))
        return
    if job.entity_type != ENTITY_TYPE_SALES_ORDER:
        logger.warning("finalize_worker_job_success unsupported entity job_id=%s", job_id)
        return
    order = sales_order_service.get_sales_order(db, job.company_id, job.entity_id)
    _set_order_wms_sent_state(order, wms_order_id)
    job.status = IntegrationJobStatus.sent
    job.attempt_count = job.attempt_count + 1
    job.last_error = None
    db.commit()


def finalize_worker_job_failure(
    db: Session,
    job_id: int,
    error: str,
    *,
    max_attempts: int,
    force_failed: bool = False,
) -> None:
    """
    Increment attempts; either return job to `pending` for retry or mark `failed`
    and mirror failure on the sales order when applicable.
    """
    job = db.get(IntegrationJob, job_id)
    if job is None or job.status != IntegrationJobStatus.processing:
        logger.warning("finalize_worker_job_failure skipped job_id=%s state=%s", job_id, getattr(job, "status", None))
        return
    msg = (error or "").strip() or "Unknown error"
    job.attempt_count = job.attempt_count + 1
    job.last_error = msg[:4000]
    terminal = force_failed or job.attempt_count >= max_attempts
    if terminal:
        job.status = IntegrationJobStatus.failed
        if job.entity_type == ENTITY_TYPE_SALES_ORDER:
            order = sales_order_service.get_sales_order(db, job.company_id, job.entity_id)
            _set_order_wms_failed_state(order, msg)
    else:
        job.status = IntegrationJobStatus.pending
    db.commit()
