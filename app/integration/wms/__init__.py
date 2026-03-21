"""
Future WMS integration (outbound).

When implemented, call from `sales_order_service` after a successful `send_to_wms`
transition — e.g. enqueue a job or POST to a WMS API. No external calls here yet.
"""
