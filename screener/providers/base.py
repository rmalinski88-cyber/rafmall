"""Abstract data provider.

Everything the screener needs from the outside world goes through this
interface, so swapping a free source for a paid one is a single new module
plus one line in ``providers/__init__.py``.

Price frames are always returned with a ``DatetimeIndex`` (ascending) and the
columns ``open, high, low, close, volume`` in lowercase.  Fundamentals are
returned as a flat ``dict`` using the canonical keys listed in ``RAW_FIELDS``;
a provider that cannot supply a field simply omits it or sets it to ``None``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]

# Canonical fundamental keys.  Providers map their own vocabulary onto these.
RAW_FIELDS = [
    "name",
    "sector",
    "industry",
    "currency",
    "market_cap",
    "total_revenue",
    "revenue_growth",
    "earnings_growth",
    "gross_margin",
    "operating_margin",
    "profit_margin",
    "return_on_equity",
    "return_on_assets",
    "debt_to_equity",  # ratio, not percent
    "current_ratio",
    "total_cash",
    "total_debt",
    "free_cashflow",
    "operating_cashflow",
    "trailing_pe",
    "forward_pe",
    "price_to_sales",
    "price_to_book",
    "ev_to_ebitda",
    "peg_ratio",
]


class ProviderError(RuntimeError):
    """Raised when a provider cannot serve a request at all."""


class DataProvider(ABC):
    """Source of prices, fundamentals and FX rates."""

    #: short name used in config and on the CLI
    name: str = "base"

    @abstractmethod
    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        """Daily OHLCV for ``ticker`` covering roughly ``lookback_days``.

        Returns an empty frame when the symbol has no usable history rather
        than raising, so one dead ticker never aborts a whole screen.
        """

    @abstractmethod
    def get_fundamentals(self, ticker: str) -> dict:
        """Flat dict of raw fundamental fields (see ``RAW_FIELDS``)."""

    @abstractmethod
    def get_fx_to_usd(self, currency: str) -> float | None:
        """How many USD one unit of ``currency`` is worth.

        ``None`` means the rate is unavailable, which callers must treat as
        "cannot compare across currencies" rather than as 1.0.
        """

    def close(self) -> None:  # pragma: no cover - providers may not need it
        """Release any held resources."""
