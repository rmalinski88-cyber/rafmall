"""Quiver Quantitative: congressional (STOCK Act) trades.

Needs an API key (``QUIVER_API_KEY``).  Quiver's field names have changed over
time, so every field is read from a list of candidate keys; a row that still
cannot be read is skipped and counted rather than crashing the run.
"""

from __future__ import annotations

from datetime import date

from ..amounts import parse_range
from ..models import BUY, SELL, Trade

LIVE_URL = "https://api.quiverquant.com/beta/live/congresstrading"

_FIELDS = {
    "actor": ("Representative", "Name", "Politician", "Senator"),
    "ticker": ("Ticker", "ticker"),
    "side": ("Transaction", "Type", "transaction"),
    "traded": ("TransactionDate", "Traded", "Date"),
    "reported": ("ReportDate", "Filed", "Disclosed"),
    "range": ("Range", "Amount Range", "Trade_Size_USD"),
    "amount": ("Amount",),
    "chamber": ("House", "Chamber"),
    "party": ("Party",),
    "description": ("Description", "Asset", "TickerType"),
}

_CHAMBER = {"representatives": "Izba", "house": "Izba", "senate": "Senat"}


class QuiverClient:
    def __init__(self, api_key: str, cache=None):
        self.api_key = api_key
        self.cache = cache

    def congress_rows(self) -> list[dict]:
        if self.cache is not None:
            hit = self.cache.get_json("quiver", "congresstrading")
            if hit is not None:
                return hit

        import requests

        response = requests.get(
            LIVE_URL,
            headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise ValueError("Quiver zwrócił nieoczekiwany format odpowiedzi")
        if self.cache is not None:
            self.cache.put_json("quiver", "congresstrading", rows)
        return rows


def parse_congress_rows(rows: list[dict], since: date | None = None) -> tuple[list[Trade], int]:
    """``(trades, skipped)``.  Exchanges and unreadable rows are skipped."""
    trades, skipped = [], 0
    for row in rows:
        trade = _parse_row(row)
        if trade is None:
            skipped += 1
            continue
        anchor = trade.reported or trade.traded
        if since is not None and anchor is not None and anchor < since:
            continue
        trades.append(trade)
    return trades, skipped


def _parse_row(row: dict) -> Trade | None:
    ticker = (_pick(row, "ticker") or "").strip().upper()
    side = _side(_pick(row, "side"))
    actor = (_pick(row, "actor") or "").strip()
    if not ticker or ticker in ("-", "N/A") or side is None or not actor:
        return None

    low, high = parse_range(_pick(row, "range"))
    if low is None:
        low, high = parse_range(_pick(row, "amount"))

    party = (_pick(row, "party") or "").strip()[:1].upper()
    chamber = _CHAMBER.get((_pick(row, "chamber") or "").strip().lower(), _pick(row, "chamber") or "")
    role = "-".join(p for p in (party, chamber) if p)

    return Trade(
        source="congress",
        actor=actor,
        role=role,
        ticker=ticker,
        side=side,
        traded=_date(_pick(row, "traded")),
        reported=_date(_pick(row, "reported")),
        amount_low=low,
        amount_high=high,
        detail=str(_pick(row, "description") or ""),
    )


def _pick(row: dict, field: str):
    for key in _FIELDS[field]:
        if row.get(key) not in (None, ""):
            return row[key]
    return None


def _side(value) -> str | None:
    text = str(value or "").lower()
    if text.startswith(("purchase", "buy")):
        return BUY
    if text.startswith(("sale", "sell")):
        return SELL
    return None  # exchanges, "received" etc.


def _date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None
