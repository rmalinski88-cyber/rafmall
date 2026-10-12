"""Which metrics a per-company view shows, and how each one is formatted.

Shared by the ``show`` command and the Obsidian export so the two never
drift apart.
"""

from __future__ import annotations

from ..analysis.scoring import LABELS
from . import format as fmt

# (key, kind): kind selects the formatter below.
FUNDAMENTAL_VIEW = [
    ("market_cap_usd", "usd"), ("revenue_growth", "pct"), ("earnings_growth", "pct"),
    ("gross_margin", "pct"), ("operating_margin", "pct"), ("profit_margin", "pct"),
    ("return_on_equity", "pct"), ("return_on_assets", "pct"), ("fcf_margin", "pct"),
    ("debt_to_equity", "num"), ("current_ratio", "num"), ("net_cash_to_mcap", "pct"),
    ("trailing_pe", "num"), ("forward_pe", "num"), ("price_to_sales", "num"),
    ("price_to_book", "num"), ("ev_to_ebitda", "num"),
]

TECHNICAL_VIEW = [
    ("px_vs_sma50", "pct"), ("px_vs_sma200", "pct"), ("sma50_vs_sma200", "pct"),
    ("rsi14", "num"), ("macd_hist_pct", "pct"),
    ("ret_1m", "pct"), ("ret_3m", "pct"), ("ret_6m", "pct"), ("ret_12m", "pct"),
    ("rs_3m", "pct"), ("rs_6m", "pct"),
    ("dist_52w_high", "pct"), ("pos_52w_range", "pct"),
    ("max_drawdown_12m", "pct"), ("atr_pct", "pct"),
]

# Metrics that are changes or spreads read better with an explicit sign.
_SIGNED_PREFIXES = ("ret_", "rs_", "px_vs", "sma50_vs", "macd", "dist_52w")


def label(key: str) -> str:
    return LABELS.get(key, key)


def format_metric(key: str, kind: str, value) -> str:
    if kind == "pct":
        return fmt.pct(value, signed=key.startswith(_SIGNED_PREFIXES))
    if kind == "num":
        return fmt.num(value, 2)
    if kind == "usd":
        return fmt.usd(value)
    return fmt.num(value)
