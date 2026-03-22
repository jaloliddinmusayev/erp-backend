"""Application service: choose client and send outbound sales order payload."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.integration.wms.client import get_wms_client
from app.integration.wms.schemas import WmsOutboundResult

logger = logging.getLogger(__name__)


def send_sales_order_payload(
    payload: dict[str, Any],
    *,
    company_id: int,
    settings: Settings | None = None,
) -> WmsOutboundResult:
    """
    Send a sales order snapshot to WMS (mock or HTTP adapter).

    `payload` is typically parsed from `IntegrationJob.payload_json`.
    """
    cfg = settings or get_settings()
    if payload.get("company_id") != company_id:
        logger.error("Payload company_id mismatch for outbound send (tenant safety)")
        return WmsOutboundResult(
            success=False,
            wms_order_id=None,
            message="Payload company_id does not match job tenant",
        )
    client = get_wms_client(cfg)
    return client.send_sales_order(payload, company_id=company_id)
