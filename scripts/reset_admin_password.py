#!/usr/bin/env python3
"""
Reset admin password from `.env` (ADMIN_EMAIL / ADMIN_PASSWORD).

Usage (repo root, DB reachable):

    python scripts/reset_admin_password.py

If the user does not exist, run `python scripts/seed.py` first.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main() -> None:
    settings = get_settings()
    email = (settings.admin_email or "").strip().lower()
    password = settings.admin_password or ""
    if not email or not password:
        print("ERROR: Set ADMIN_EMAIL and ADMIN_PASSWORD in .env", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.scalars(select(User).where(User.email == email)).first()
        if user is None:
            print(f"ERROR: No user with email {email!r}. Run: python scripts/seed.py", file=sys.stderr)
            sys.exit(1)
        user.password_hash = hash_password(password)
        user.is_active = True
        db.commit()
        print(f"OK: password updated for {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
