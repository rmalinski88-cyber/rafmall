"""Yahoo Finance provider (free, via ``yfinance``).

Covers every exchange in the Asian humanoid-robotics universe: Tokyo (``.T``),
Korea (``.KS`` / ``.KQ``), Taiwan (``.TW`` / ``.TWO``), Hong Kong (``.HK``) and
the mainland boards (``.SS`` / ``.SZ``).

Yahoo's fundamentals are best-effort: coverage is good for the large Japanese
and Taiwanese names and patchy for small-cap KOSDAQ and mainland listings.
Missing fields are left out rather than guessed; the scorer handles gaps.
"""

from __future__ import annotations

import time

import pandas as pd

from .base import PRICE_COLUMNS, DataProvider, ProviderError

# Yahoo reports debtToEquity in percent; everything else that we consume is
# already a fraction.
_PERCENT_FIELDS = {"debtToEquity"}

_INFO_MAP = {
    "name": ("shortName", "longName"),
    "sector": ("sector",),
    "industry": ("industry",),
    "currency": ("currency",),
    "market_cap": ("marketCap",),
    "total_revenue": ("totalRevenue",),
    "revenue_growth": ("revenueGrowth",),
    "earnings_growth": ("earningsGrowth", "earningsQuarterlyGrowth"),
    "gross_margin": ("grossMargins",),
    "operating_margin": ("operatingMargins",),
    "profit_margin": ("profitMargins",),
    "return_on_equity": ("returnOnEquity",),
    "return_on_assets": ("returnOnAssets",),
    "debt_to_equity": ("debtToEquity",),
    "current_ratio": ("currentRatio",),
    "total_cash": ("totalCash",),
    "total_debt": ("totalDebt",),
    "free_cashflow": ("freeCashflow",),
    "operating_cashflow": ("operatingCashflow",),
    "trailing_pe": ("trailingPE",),
    "forward_pe": ("forwardPE",),
    "price_to_sales": ("priceToSalesTrailing12Months",),
    "price_to_book": ("priceToBook",),
    "ev_to_ebitda": ("enterpriseToEbitda",),
    "peg_ratio": ("trailingPegRatio", "pegRatio"),
    # Instrument identity, used by the tracker to tell stocks, ETFs and crypto apart.
    "quote_type": ("quoteType",),
    "category": ("category",),
    "total_assets": ("totalAssets",),
}


class YahooProvider(DataProvider):
    name = "yahoo"

    def __init__(self, cache=None, throttle_seconds: float = 0.4):
        self.cache = cache
        self.throttle_seconds = throttle_seconds
        self._fx_cache: dict[str, float | None] = {}
        try:
            import yfinance  # noqa: F401
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderError(
                "yfinance is not installed - run: pip install -r requirements.txt"
            ) from exc

    # -- prices --------------------------------------------------------

    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        if self.cache is not None:
            cached = self.cache.get_frame("prices", ticker)
            if cached is not None:
                return cached

        import yfinance as yf

        # Ask for calendar days with headroom: ~250 trading days per year.
        period = f"{max(int(lookback_days * 1.5), 30)}d"
        try:
            raw = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        except Exception:
            return pd.DataFrame(columns=PRICE_COLUMNS)
        finally:
            self._throttle()

        frame = _normalise_prices(raw)
        if not frame.empty and self.cache is not None:
            self.cache.put_frame("prices", ticker, frame)
        return frame

    # -- fundamentals --------------------------------------------------

    def get_fundamentals(self, ticker: str) -> dict:
        if self.cache is not None:
            cached = self.cache.get_json("fundamentals", ticker)
            if cached is not None:
                return cached

        import yfinance as yf

        try:
            info = yf.Ticker(ticker).info or {}
        except Exception:
            info = {}
        finally:
            self._throttle()

        payload = _map_info(info)
        if payload and self.cache is not None:
            self.cache.put_json("fundamentals", ticker, payload)
        return payload

    # -- fx ------------------------------------------------------------

    def get_fx_to_usd(self, currency: str) -> float | None:
        if not currency:
            return None
        currency = currency.upper()
        if currency == "USD":
            return 1.0
        if currency in self._fx_cache:
            return self._fx_cache[currency]

        if self.cache is not None:
            cached = self.cache.get_json("fx", currency)
            if cached is not None and cached.get("rate"):
                self._fx_cache[currency] = cached["rate"]
                return cached["rate"]

        import yfinance as yf

        # "JPY=X" quotes JPY per 1 USD, so one JPY is worth 1/rate USD.
        try:
            hist = yf.Ticker(f"{currency}=X").history(period="5d")
            per_usd = float(hist["Close"].dropna().iloc[-1]) if not hist.empty else None
        except Exception:
            per_usd = None
        finally:
            self._throttle()

        rate = (1.0 / per_usd) if per_usd else None
        self._fx_cache[currency] = rate
        if rate and self.cache is not None:
            self.cache.put_json("fx", currency, {"rate": rate})
        return rate

    def _throttle(self) -> None:
        if self.throttle_seconds:
            time.sleep(self.throttle_seconds)


def _normalise_prices(raw: pd.DataFrame) -> pd.DataFrame:
    """Lowercase Yahoo's columns and drop rows without a close."""
    if raw is None or raw.empty:
        return pd.DataFrame(columns=PRICE_COLUMNS)

    frame = raw.rename(columns={c: str(c).lower() for c in raw.columns})
    missing = [c for c in PRICE_COLUMNS if c not in frame.columns]
    if missing:
        return pd.DataFrame(columns=PRICE_COLUMNS)

    frame = frame[PRICE_COLUMNS].copy()
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    frame = frame[frame["close"].notna()]
    return frame.sort_index()


def _map_info(info: dict) -> dict:
    """Translate a Yahoo ``info`` blob into canonical fundamental fields."""
    out: dict = {}
    for canonical, candidates in _INFO_MAP.items():
        for key in candidates:
            value = info.get(key)
            if value in (None, "", "Infinity"):
                continue
            if key in _PERCENT_FIELDS:
                try:
                    value = float(value) / 100.0
                except (TypeError, ValueError):
                    continue
            out[canonical] = value
            break
    return out
