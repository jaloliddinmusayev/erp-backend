"""DTOs for WMS outbound calls (adapter boundary)."""

from pydantic import BaseModel, Field


class WmsOutboundResult(BaseModel):
    """Normalized result from any WMS client implementation."""

    success: bool
    wms_order_id: str | None = None
    message: str = ""


class WmsSalesOrderOutboundPayload(BaseModel):
    """Typed view of the JSON we store on IntegrationJob (subset for validation)."""

    entity_type: str
    sales_order_id: int
    company_id: int
    order_number: str
    order_date: str
    client_id: int
    branch_id: int | None = None
    total_amount: str
    lines: list[dict] = Field(default_factory=list)
