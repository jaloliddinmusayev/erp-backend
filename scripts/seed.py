#!/usr/bin/env python3
"""
Load initial demo company, admin role, and admin@erp.uz user.

Usage (from repository root, where `app/` lives):

    python scripts/seed.py

Requires DATABASE_URL in environment or `.env` (same as the API).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root = parent of scripts/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.services.bootstrap_service import run_initial_seed  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        out = run_initial_seed(db)
    finally:
        db.close()
    print("Seed finished:", out)


if __name__ == "__main__":
    main()
