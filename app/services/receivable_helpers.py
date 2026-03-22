"""Derived AR aging helpers (no DB columns)."""

from datetime import date
from decimal import Decimal

from app.models.invoice import Invoice
from app.schemas.receivable import AgingBucket


def invoice_aging_base_date(invoice: Invoice) -> date:
    """Due date if set, otherwise invoice date (per product rule)."""
    return invoice.due_date if invoice.due_date is not None else invoice.invoice_date


def calculate_invoice_overdue_days(invoice: Invoice, as_of_date: date) -> int:
    """
    Whole days past the aging base date. Not overdue until strictly after base date.
    If as_of is before base date, returns 0.
    """
    base = invoice_aging_base_date(invoice)
    if as_of_date <= base:
        return 0
    return (as_of_date - base).days


def determine_aging_bucket(overdue_days: int) -> AgingBucket:
    if overdue_days <= 0:
        return AgingBucket.current
    if overdue_days <= 30:
        return AgingBucket.days_1_30
    if overdue_days <= 60:
        return AgingBucket.days_31_60
    if overdue_days <= 90:
        return AgingBucket.days_61_90
    return AgingBucket.days_90_plus


def bucket_add(target: dict[AgingBucket, Decimal], bucket: AgingBucket, amount: Decimal) -> None:
    target[bucket] = target.get(bucket, Decimal("0")) + amount
