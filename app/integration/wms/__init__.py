"""
WMS integration package.

- `schemas` — outbound result / payload DTOs
- `client` — `MockWmsClient`, `HttpWmsClient` (TODO: vendor contract)
- `service` — `send_sales_order_payload` used by the integration worker

Background worker: `python scripts/run_worker.py` (claims `IntegrationJob` rows, calls adapter).
"""
