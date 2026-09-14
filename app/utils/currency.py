"""Zambian Kwacha (ZMK) formatting."""

CURRENCY_CODE = "ZMK"
CURRENCY_SYMBOL = "ZMK"


def format_kwacha(amount, decimals=2) -> str:
    """Format a numeric amount as Zambian Kwacha."""
    if amount is None:
        return f"{CURRENCY_SYMBOL} 0.00"
    value = float(amount)
    if decimals == 0:
        return f"{CURRENCY_SYMBOL} {value:,.0f}"
    return f"{CURRENCY_SYMBOL} {value:,.2f}"
