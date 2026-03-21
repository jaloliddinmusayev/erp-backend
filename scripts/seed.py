#!/usr/bin/env python3
"""
Load initial demo company, admin role, and admin user.

Usage (from repository root):

    python scripts/seed.py

Required in `.env` or environment for admin user creation:
    ADMIN_EMAIL
    ADMIN_PASSWORD

Optional: ADMIN_FULL_NAME (default: Super Admin)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.services.bootstrap_service import run_initial_seed  # noqa: E402


def main() -> None:
    s = get_settings()
    if not (s.admin_email or "").strip() or not (s.admin_password or "").strip():
        print("ERROR: Set ADMIN_EMAIL and ADMIN_PASSWORD in .env or environment.", file=sys.stderr)
        sys.exit(1)
    db = SessionLocal()
    try:
        out = run_initial_seed(db, settings=s)
    finally:
        db.close()
    print("Seed finished:", out)


if __name__ == "__main__":
    main()
