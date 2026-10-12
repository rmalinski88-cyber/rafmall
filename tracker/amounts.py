"""Parsing of STOCK Act amount brackets.

Members of Congress disclose a value range, not an amount:
``"$1,001 - $15,000"``, ``"$1,000,001 - $5,000,000"``, ``"Over $50,000,000"``.
The midpoint is used for sums; the bracket itself is shown in reports so the
uncertainty is never hidden.
"""

from __future__ import annotations

import re

_NUMBER = re.compile(r"\$?\s*([\d][\d,]*(?:\.\d+)?)")


def parse_range(text) -> tuple[float | None, float | None]:
    """``"$1,001 - $15,000"`` -> ``(1001.0, 15000.0)``; unknown -> ``(None, None)``."""
    if text is None:
        return None, None
    if isinstance(text, (int, float)):
        return float(text), float(text)

    raw = str(text).strip()
    numbers = [float(n.replace(",", "")) for n in _NUMBER.findall(raw)]
    if not numbers:
        return None, None

    lowered = raw.lower()
    if len(numbers) == 1:
        # "Over $50,000,000" and "$50,000,001 +" are open-ended.
        if "over" in lowered or "+" in raw or "powyżej" in lowered:
            return numbers[0], None
        return numbers[0], numbers[0]
    low, high = numbers[0], numbers[1]
    return (low, high) if low <= high else (high, low)


def format_range(low: float | None, high: float | None) -> str:
    """Compact Polish rendering: ``1 tys. – 15 tys. USD``."""
    if low is None:
        return "—"
    if high is None:
        return f"> {_short(low)} USD"
    if high == low:
        return f"{_short(low)} USD"
    return f"{_short(low)} – {_short(high)} USD"


def _short(value: float) -> str:
    for threshold, suffix in ((1e9, "mld"), (1e6, "mln"), (1e3, "tys.")):
        if abs(value) >= threshold:
            scaled = value / threshold
            text = f"{scaled:.1f}".rstrip("0").rstrip(".").replace(".", ",")
            return f"{text} {suffix}"
    return f"{value:,.0f}".replace(",", " ")
