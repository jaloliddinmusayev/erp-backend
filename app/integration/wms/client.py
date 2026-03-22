"""Pluggable WMS HTTP clients. Replace `HttpWmsClient` body when the vendor contract is fixed."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Protocol

import httpx

from app.core.config import Settings
from app.integration.wms.schemas import WmsOutboundResult

logger = logging.getLogger(__name__)


class WmsOutboundClient(Protocol):
    def send_sales_order(self, payload: dict[str, Any], *, company_id: int) -> WmsOutboundResult:
        """POST sales order snapshot to WMS; must be tenant-safe (company_id for headers/path)."""
        ...


class MockWmsClient:
    """Deterministic fake WMS for dev/tests; no network."""

    def send_sales_order(self, payload: dict[str, Any], *, company_id: int) -> WmsOutboundResult:
        oid = payload.get("sales_order_id", "?")
        wms_id = f"MOCK-{oid}-{uuid.uuid4().hex[:8]}"
        logger.info("MockWmsClient: accepted sales_order_id=%s company_id=%s -> %s", oid, company_id, wms_id)
        return WmsOutboundResult(success=True, wms_order_id=wms_id, message="mock_ok")


class HttpWmsClient:
    """
    Real HTTP outbound (skeleton).

    TODO: final URL path, auth scheme (OAuth2, API key, mTLS), idempotency key, error mapping.
    """

    def __init__(self, *, base_url: str, api_key: str, timeout_seconds: float = 30.0) -> None:
        self._base = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds

    def send_sales_order(self, payload: dict[str, Any], *, company_id: int) -> WmsOutboundResult:
        # TODO: align with WMS contract — example placeholder path:
        url = f"{self._base}/api/v1/outbound/sales-orders"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "X-Company-Id": str(company_id),
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("HttpWmsClient HTTP error: %s", exc)
            return WmsOutboundResult(success=False, wms_order_id=None, message=str(exc)[:2000])

        if response.status_code >= 400:
            body = (response.text or "")[:2000]
            logger.warning(
                "HttpWmsClient error status=%s body=%s",
                response.status_code,
                body,
            )
            return WmsOutboundResult(
                success=False,
                wms_order_id=None,
                message=f"HTTP {response.status_code}: {body}",
            )

        # TODO: parse real JSON — expect { "wms_order_id": "..." } or similar
        try:
            data = response.json()
        except Exception:
            return WmsOutboundResult(
                success=False,
                wms_order_id=None,
                message="WMS response was not valid JSON",
            )
        wms_id = data.get("wms_order_id") or data.get("id")
        if not wms_id:
            return WmsOutboundResult(
                success=False,
                wms_order_id=None,
                message="WMS response missing wms_order_id",
            )
        return WmsOutboundResult(success=True, wms_order_id=str(wms_id), message="ok")


def get_wms_client(settings: Settings) -> WmsOutboundClient:
    if settings.wms_mock_mode:
        return MockWmsClient()
    if not settings.wms_base_url.strip():
        logger.error("WMS mock disabled but WMS_BASE_URL is empty; using mock to avoid crash")
        return MockWmsClient()
    return HttpWmsClient(
        base_url=settings.wms_base_url,
        api_key=settings.wms_api_key,
        timeout_seconds=settings.wms_http_timeout_seconds,
    )
