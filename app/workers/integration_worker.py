"""
Outbound integration worker: claims pending `IntegrationJob` rows and pushes to WMS adapters.

Run standalone: `python scripts/run_worker.py` (or import `run_worker_cycle` from a scheduler).
"""

from __future__ import annotations

import json
import logging
import time

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import SessionLocal
from app.models.integration_job import (
    ENTITY_TYPE_SALES_ORDER,
    EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER,
    IntegrationJob,
    IntegrationJobStatus,
)
from app.integration.wms.service import send_sales_order_payload
from app.services import integration_service

logger = logging.getLogger(__name__)


def run_worker_cycle(settings: Settings | None = None) -> int:
    """
    One pass: reclaim stale leases, claim a batch, process each job in its own session.
    Returns number of jobs processed (success or terminal failure).
    """
    cfg = settings or get_settings()
    processed = 0

    db = SessionLocal()
    try:
        reclaimed = integration_service.reclaim_stale_processing_jobs(
            db, stale_after_seconds=cfg.integration_job_stale_processing_seconds
        )
        if reclaimed:
            logger.info("Reclaimed %s stale processing integration job(s)", reclaimed)

        job_ids = integration_service.claim_pending_jobs_for_worker(
            db,
            limit=cfg.integration_worker_batch_size,
            max_attempts=cfg.integration_job_max_attempts,
        )
    finally:
        db.close()

    if not job_ids:
        logger.debug("No pending integration jobs to process")
        return 0

    logger.info("Picked %s integration job(s) for processing: %s", len(job_ids), job_ids)

    for job_id in job_ids:
        processed += _process_single_job(job_id, cfg)

    return processed


def _process_single_job(job_id: int, cfg: Settings) -> int:
    db: Session = SessionLocal()
    try:
        job = db.get(IntegrationJob, job_id)
        if job is None:
            logger.warning("Job %s disappeared after claim", job_id)
            return 1
        if job.status != IntegrationJobStatus.processing:
            logger.warning("Job %s not in processing state (skip): %s", job_id, job.status)
            return 1

        if job.event_type != EVENT_TYPE_WMS_OUTBOUND_SALES_ORDER:
            logger.warning("Unsupported event_type=%s for job %s", job.event_type, job_id)
            integration_service.finalize_worker_job_failure(
                db,
                job_id,
                f"Unsupported event_type: {job.event_type}",
                max_attempts=cfg.integration_job_max_attempts,
                force_failed=True,
            )
            return 1

        if job.entity_type != ENTITY_TYPE_SALES_ORDER:
            logger.warning("Unsupported entity_type=%s for job %s", job.entity_type, job_id)
            integration_service.finalize_worker_job_failure(
                db,
                job_id,
                f"Unsupported entity_type: {job.entity_type}",
                max_attempts=cfg.integration_job_max_attempts,
                force_failed=True,
            )
            return 1

        try:
            payload = json.loads(job.payload_json)
        except json.JSONDecodeError as exc:
            logger.exception("Invalid payload_json for job %s", job_id)
            integration_service.finalize_worker_job_failure(
                db,
                job_id,
                f"Invalid payload JSON: {exc}",
                max_attempts=cfg.integration_job_max_attempts,
                force_failed=True,
            )
            return 1

        cid = payload.get("company_id")
        if cid != job.company_id:
            logger.error("Tenant mismatch job %s: payload company_id=%s job company_id=%s", job_id, cid, job.company_id)
            integration_service.finalize_worker_job_failure(
                db,
                job_id,
                "Payload company_id does not match integration job company_id",
                max_attempts=cfg.integration_job_max_attempts,
                force_failed=True,
            )
            return 1

        logger.info(
            "Sending job %s to WMS adapter (company_id=%s entity_id=%s attempt_count=%s)",
            job_id,
            job.company_id,
            job.entity_id,
            job.attempt_count,
        )
        result = send_sales_order_payload(payload, company_id=job.company_id, settings=cfg)

        if result.success and result.wms_order_id:
            integration_service.finalize_worker_job_success(db, job_id, result.wms_order_id)
            logger.info("Job %s succeeded wms_order_id=%s", job_id, result.wms_order_id)
        else:
            msg = result.message or "WMS reported failure"
            integration_service.finalize_worker_job_failure(
                db, job_id, msg, max_attempts=cfg.integration_job_max_attempts
            )
            logger.warning("Job %s failed: %s", job_id, msg[:500])
        return 1
    except Exception as exc:
        logger.exception("Unhandled error processing job %s", job_id)
        try:
            integration_service.finalize_worker_job_failure(
                db,
                job_id,
                str(exc)[:2000],
                max_attempts=cfg.integration_job_max_attempts,
            )
        except Exception:
            db.rollback()
        return 1
    finally:
        db.close()


def run_worker_loop(settings: Settings | None = None) -> None:
    cfg = settings or get_settings()
    interval = cfg.integration_worker_loop_seconds
    if interval <= 0:
        run_worker_cycle(cfg)
        return
    logger.info("Integration worker loop every %s s", interval)
    while True:
        try:
            run_worker_cycle(cfg)
        except Exception:
            logger.exception("Worker cycle error")
        time.sleep(interval)
