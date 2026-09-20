"""Derived fundamental metrics.

Takes a provider's raw field dict and produces the normalised set the scorer
consumes.  Two rules run through all of it:

* A multiple computed off negative earnings is meaningless, so a negative or
  absurd P/E becomes ``None`` rather than a number that would rank well when
  inverted.  Much of this sector is pre-profit - that has to be handled, not
  papered over.
* Nothing is imputed.  A missing field stays missing and the scorer
  renormalises the weights it actually had.
"""

from __future__ import annotations

import math

# Above these, a multiple carries no information - it is noise from a near-zero
# denominator, and clamping it would fake precision.
_MAX_SANE = {
    "trailing_pe": 300.0,
    "forward_pe": 300.0,
    "ev_to_ebitda": 200.0,
    "price_to_sales": 100.0,
    "price_to_book": 100.0,
    "peg_ratio": 20.0,
}


def _number(value) -> float | None:
    """Coerce to a finite float, or ``None``."""
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _positive_multiple(value, field: str) -> float | None:
    """A valuation multiple, kept only when positive and within sane bounds."""
    number = _number(value)
    if number is None or number <= 0:
        return None
    return number if number <= _MAX_SANE.get(field, float("inf")) else None


def compute_fundamental_metrics(raw: dict) -> dict:
    """Normalised fundamentals for one ticker."""
    raw = raw or {}
    out: dict = {
        "name": raw.get("name"),
        "sector": raw.get("sector"),
        "industry": raw.get("industry"),
        "currency": (raw.get("currency") or "").upper() or None,
    }

    out["market_cap"] = _number(raw.get("market_cap"))
    out["total_revenue"] = _number(raw.get("total_revenue"))

    # Growth and profitability pass through as-is: negatives are real signal.
    for field in (
        "revenue_growth",
        "earnings_growth",
        "gross_margin",
        "operating_margin",
        "profit_margin",
        "return_on_equity",
        "return_on_assets",
        "debt_to_equity",
        "current_ratio",
    ):
        out[field] = _number(raw.get(field))

    for field in ("trailing_pe", "forward_pe", "ev_to_ebitda", "price_to_sales", "price_to_book", "peg_ratio"):
        out[field] = _positive_multiple(raw.get(field), field)

    revenue = out["total_revenue"]
    free_cashflow = _number(raw.get("free_cashflow"))
    out["free_cashflow"] = free_cashflow
    out["fcf_margin"] = (free_cashflow / revenue) if (free_cashflow is not None and revenue) else None

    cash, debt, market_cap = (
        _number(raw.get("total_cash")),
        _number(raw.get("total_debt")),
        out["market_cap"],
    )
    out["net_cash"] = (cash - debt) if (cash is not None and debt is not None) else None
    out["net_cash_to_mcap"] = (
        (out["net_cash"] / market_cap) if (out["net_cash"] is not None and market_cap) else None
    )

    # Earnings yield is the inverse of P/E and, unlike P/E, stays well behaved
    # as earnings approach zero - it is what the scorer actually ranks on.
    out["earnings_yield"] = (1.0 / out["trailing_pe"]) if out["trailing_pe"] else None
    out["is_profitable"] = (out["profit_margin"] is not None and out["profit_margin"] > 0) or (
        out["trailing_pe"] is not None
    )
    return out
