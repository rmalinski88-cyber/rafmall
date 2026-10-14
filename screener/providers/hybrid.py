"""Hybrid provider: Yahoo price history + TradingView fundamentals.

Each source does what it is best at.  Yahoo has daily history, so the
technical indicators are computed locally and the report gets its price
charts; TradingView has the more complete and consistent fundamentals for
Asian listings, fetched for the whole universe in one request.

When Yahoo has no history for a symbol, the pipeline falls back to the
indicators TradingView computes itself, so a ticker never drops out just
because one source missed it.
"""

from __future__ import annotations

import pandas as pd

from .base import DataProvider
from .tradingview import TradingViewProvider
from .yahoo import YahooProvider


class HybridProvider(DataProvider):
    name = "hybrid"

    def __init__(self, cache=None, prices: DataProvider | None = None,
                 fundamentals: TradingViewProvider | None = None):
        self.prices = prices or YahooProvider(cache=cache)
        self.fundamentals = fundamentals or TradingViewProvider(cache=cache)

    def prefetch(self, tickers: list[str]) -> None:
        self.fundamentals.prefetch(tickers)

    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        return self.prices.get_prices(ticker, lookback_days)

    def get_fundamentals(self, ticker: str) -> dict:
        data = self.fundamentals.get_fundamentals(ticker)
        return data or self.prices.get_fundamentals(ticker)

    def get_technicals(self, ticker: str) -> dict | None:
        # Only asked when Yahoo returned no history for this ticker.
        return self.fundamentals.get_technicals(ticker)

    def get_fx_to_usd(self, currency: str) -> float | None:
        return self.fundamentals.get_fx_to_usd(currency) or self.prices.get_fx_to_usd(currency)

    def diagnostics(self) -> list[str]:
        return [*self.fundamentals.diagnostics(), *self.prices.diagnostics()]

    def raw_row(self, ticker: str) -> dict | None:
        return self.fundamentals.raw_row(ticker)
