"""Shared decimal quantization for money fields (AR, payments, invoices)."""

from decimal import ROUND_HALF_UP, Decimal

MONEY_QUANT = Decimal("0.0001")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
