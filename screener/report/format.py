"""Value formatting shared by the console and HTML reports (Polish locale)."""

from __future__ import annotations

import math

DASH = "—"


def _finite(value) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def pct(value, digits: int = 1, signed: bool = False) -> str:
    """A fraction rendered as a percentage: ``0.153`` -> ``15,3%``."""
    number = _finite(value)
    if number is None:
        return DASH
    text = f"{number * 100:+.{digits}f}%" if signed else f"{number * 100:.{digits}f}%"
    return text.replace(".", ",")


def num(value, digits: int = 1) -> str:
    number = _finite(value)
    if number is None:
        return DASH
    return f"{number:.{digits}f}".replace(".", ",")


def score(value) -> str:
    number = _finite(value)
    return DASH if number is None else f"{number:.0f}"


def usd(value) -> str:
    """Compact USD magnitude: ``bln`` = 10^12, ``mld`` = 10^9, ``mln`` = 10^6."""
    number = _finite(value)
    if number is None:
        return DASH
    for threshold, suffix in ((1e12, "bln"), (1e9, "mld"), (1e6, "mln")):
        if abs(number) >= threshold:
            return f"{number / threshold:.1f} {suffix} USD".replace(".", ",")
    return f"{number:,.0f} USD".replace(",", " ")
