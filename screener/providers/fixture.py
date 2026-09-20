"""Deterministic offline provider.

Generates reproducible synthetic prices and fundamentals from a hash of the
ticker, so the whole pipeline - indicators, scoring, filters, report - can be
exercised and tested without a network connection.  Same ticker always yields
the same data.

It is a test double, not a data source: never read an investment conclusion
out of a fixture run.
"""

from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

from .base import PRICE_COLUMNS, DataProvider

# Plausible USD value of one unit of each currency, for the filter maths.
_FX = {
    "USD": 1.0,
    "JPY": 0.0064,
    "KRW": 0.00072,
    "TWD": 0.031,
    "HKD": 0.128,
    "CNY": 0.139,
}


_SUFFIX_CURRENCY = {
    ".T": "JPY",
    ".KS": "KRW",
    ".KQ": "KRW",
    ".TW": "TWD",
    ".TWO": "TWD",
    ".HK": "HKD",
    ".SS": "CNY",
    ".SZ": "CNY",
}


def _seed(ticker: str) -> int:
    return zlib.crc32(ticker.encode("utf-8")) & 0xFFFFFFFF


def _currency_for(ticker: str) -> str:
    for suffix, currency in _SUFFIX_CURRENCY.items():
        if ticker.upper().endswith(suffix):
            return currency
    return "USD"


class FixtureProvider(DataProvider):
    name = "fixture"

    def __init__(self, cache=None, trading_days: int = 520):
        self.cache = cache  # accepted for interface parity; nothing to cache
        self.trading_days = trading_days

    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        rng = np.random.default_rng(_seed(ticker))
        n = min(self.trading_days, max(int(lookback_days), 30))

        # Annualised drift between -25% and +60%, vol between 20% and 70%.
        drift = rng.uniform(-0.25, 0.60) / 252.0
        vol = rng.uniform(0.20, 0.70) / np.sqrt(252.0)

        shocks = rng.normal(drift, vol, size=n)
        close = 100.0 * np.exp(np.cumsum(shocks))

        intraday = np.abs(rng.normal(0.0, vol * 0.6, size=n))
        high = close * (1.0 + intraday)
        low = close * (1.0 - intraday)
        open_ = np.concatenate([[close[0]], close[:-1]])
        volume = rng.lognormal(mean=13.0, sigma=0.35, size=n).round()

        index = pd.bdate_range(end=pd.Timestamp("2026-09-18"), periods=n)
        frame = pd.DataFrame(
            {
                "open": open_,
                "high": np.maximum.reduce([high, open_, close]),
                "low": np.minimum.reduce([low, open_, close]),
                "close": close,
                "volume": volume,
            },
            index=index,
        )
        return frame[PRICE_COLUMNS]

    def get_fundamentals(self, ticker: str) -> dict:
        rng = np.random.default_rng(_seed(ticker) ^ 0xA5A5)

        # Roughly a third of the universe is pre-profit, as in the real sector.
        profitable = rng.random() > 0.33
        revenue = float(rng.lognormal(mean=21.0, sigma=1.6))
        profit_margin = float(rng.uniform(0.03, 0.22)) if profitable else float(rng.uniform(-0.45, -0.01))

        payload = {
            "name": f"Fixture {ticker}",
            "sector": "Industrials",
            "industry": "Robotics",
            "currency": _currency_for(ticker),
            "market_cap": float(rng.lognormal(mean=22.5, sigma=1.5)),
            "total_revenue": revenue,
            "revenue_growth": float(rng.uniform(-0.15, 0.85)),
            "earnings_growth": float(rng.uniform(-0.50, 1.40)),
            "gross_margin": float(rng.uniform(0.18, 0.62)),
            "operating_margin": profit_margin + float(rng.uniform(0.0, 0.05)),
            "profit_margin": profit_margin,
            "return_on_equity": float(rng.uniform(0.02, 0.28)) if profitable else float(rng.uniform(-0.30, 0.0)),
            "return_on_assets": float(rng.uniform(0.01, 0.15)) if profitable else float(rng.uniform(-0.18, 0.0)),
            "debt_to_equity": float(rng.uniform(0.0, 1.8)),
            "current_ratio": float(rng.uniform(0.8, 3.5)),
            "total_cash": float(rng.lognormal(mean=20.0, sigma=1.2)),
            "total_debt": float(rng.lognormal(mean=19.5, sigma=1.4)),
            "free_cashflow": revenue * float(rng.uniform(-0.15, 0.20)),
            "operating_cashflow": revenue * float(rng.uniform(-0.05, 0.28)),
            "price_to_sales": float(rng.uniform(0.6, 14.0)),
            "price_to_book": float(rng.uniform(0.7, 11.0)),
        }

        # Valuation multiples only exist for profitable companies.
        if profitable:
            payload["trailing_pe"] = float(rng.uniform(8.0, 75.0))
            payload["forward_pe"] = payload["trailing_pe"] * float(rng.uniform(0.6, 1.1))
            payload["ev_to_ebitda"] = float(rng.uniform(5.0, 40.0))
            payload["peg_ratio"] = float(rng.uniform(0.4, 4.0))

        # Drop a couple of fields at random so gap handling stays exercised.
        droppable = ["current_ratio", "return_on_assets", "operating_cashflow", "price_to_book"]
        for field in droppable:
            if rng.random() < 0.25:
                payload.pop(field, None)

        return payload

    def get_fx_to_usd(self, currency: str) -> float | None:
        return _FX.get((currency or "").upper())
