"""Portfolio and watchlist files."""

from __future__ import annotations

import csv
from pathlib import Path


def load_symbols(path: str | Path) -> list[dict]:
    """Rows of a CSV with at least a ``ticker`` column; ``#`` lines are comments."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        lines = [line for line in handle if line.strip() and not line.lstrip().startswith("#")]
    rows = []
    for row in csv.DictReader(lines):
        ticker = (row.get("ticker") or "").strip().upper()
        if ticker:
            rows.append({**{k: (v or "").strip() for k, v in row.items() if k}, "ticker": ticker})
    return rows


def tickers(rows: list[dict]) -> set[str]:
    return {r["ticker"] for r in rows}
