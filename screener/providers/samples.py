"""Real price history kept in the repo, for offline replay and rule tuning.

``python -m tracker dump SYMBOL`` on a machine with network prints the CSV;
saved as ``data/samples/<SYMBOL>.csv`` it lets a session without network run
``replay`` on real bars.  Anything not in the folder falls back to the
synthetic fixture so the rest of a run still works.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import PRICE_COLUMNS, DataProvider
from .fixture import FixtureProvider


class SamplesProvider(DataProvider):
    name = "samples"

    def __init__(self, cache=None, root: str | Path = "data/samples"):
        self.root = Path(root)
        self._fixture = FixtureProvider()

    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        path = self.root / f"{ticker.upper()}.csv"
        if not path.exists():
            return self._fixture.get_prices(ticker, lookback_days)
        frame = pd.read_csv(path, index_col=0)
        frame.index = pd.to_datetime(frame.index)
        frame.columns = [c.lower() for c in frame.columns]
        frame = frame[PRICE_COLUMNS].sort_index()
        return frame.tail(int(lookback_days * 1.5))

    def get_fundamentals(self, ticker: str) -> dict:
        return self._fixture.get_fundamentals(ticker)

    def get_fx_to_usd(self, currency: str) -> float | None:
        return self._fixture.get_fx_to_usd(currency)
