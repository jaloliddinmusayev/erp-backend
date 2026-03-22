#!/usr/bin/env python3
"""
Run the outbound integration worker (WMS sync jobs).

Usage (repo root):

    python scripts/run_worker.py

Environment (see `.env.example`):
- `DATABASE_URL` — same as API
- `WMS_MOCK_MODE` — default true (no HTTP)
- `INTEGRATION_WORKER_LOOP_SECONDS` — 0 = one batch then exit; >0 = sleep loop (daemon-style)

Render: add a **Background Worker** with start command:

    python scripts/run_worker.py

(use the same `DATABASE_URL` and env as the web service)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.workers.integration_worker import run_worker_cycle, run_worker_loop  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = get_settings()
    if settings.integration_worker_loop_seconds > 0:
        run_worker_loop(settings)
    else:
        n = run_worker_cycle(settings)
        logging.getLogger(__name__).info("Integration worker cycle finished; processed job slots: %s", n)


if __name__ == "__main__":
    main()
