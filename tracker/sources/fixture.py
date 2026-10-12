"""Deterministic offline feed.

Synthetic congressional, insider and 13F data built from fixed seeds, so the
whole tracker - signals, state, reports - runs and is tested without a
network.  It is a test double: the people and amounts are invented, never
read anything into them.
"""

from __future__ import annotations

import zlib
from datetime import date, timedelta

import numpy as np

from ..amounts import parse_range
from ..funds import diff_holdings
from ..models import BUY, SELL, Fund, FundReport, Holding, Trade
from .base import TradeFeed

# Anchored to the real date so the CLI's look-back windows always find data;
# the random draws themselves do not depend on it.
TODAY = date.today()

_TICKERS = {
    "NVDA": "NVIDIA Corp", "MSFT": "Microsoft Corp", "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.", "META": "Meta Platforms, Inc.", "AMZN": "Amazon.com, Inc.",
    "TSLA": "Tesla, Inc.", "AVGO": "Broadcom Inc.", "PG": "Procter & Gamble Co",
    "KO": "Coca-Cola Co", "AXP": "American Express Co", "OXY": "Occidental Petroleum Corp",
    "PLTR": "Palantir Technologies Inc.", "AMD": "Advanced Micro Devices Inc",
    "SPY": "SPDR S&P 500 ETF Trust", "QQQ": "Invesco QQQ Trust",
}

_BRACKETS = ["$1,001 - $15,000", "$15,001 - $50,000", "$50,001 - $100,000",
             "$100,001 - $250,000", "$250,001 - $500,000", "$1,000,001 - $5,000,000"]

_MEMBERS = [("Członek A", "D-Izba"), ("Członek B", "R-Izba"), ("Członek C", "R-Senat"),
            ("Członek D", "D-Senat"), ("Członek E", "R-Izba")]

_INSIDERS = [("Insider CEO", "Chief Executive Officer"), ("Insider CFO", "Chief Financial Officer"),
             ("Insider Dyrektor", "Director"), ("Insider COO", "Chief Operating Officer")]


def _rng(*parts) -> np.random.Generator:
    return np.random.default_rng(zlib.crc32("|".join(map(str, parts)).encode()) & 0xFFFFFFFF)


class FixtureFeed(TradeFeed):
    name = "fixture"

    def __init__(self, config: dict | None = None, fresh_cache=None, archive_cache=None):
        super().__init__()

    def congress_trades(self, since: date) -> list[Trade]:
        rng = _rng("congress")
        trades = []
        tickers = [t for t in _TICKERS if t not in ("SPY", "QQQ")]
        for i in range(40):
            member, role = _MEMBERS[int(rng.integers(len(_MEMBERS)))]
            ticker = tickers[int(rng.integers(len(tickers)))]
            traded = TODAY - timedelta(days=int(rng.integers(5, 70)))
            reported = traded + timedelta(days=int(rng.integers(3, 45)))
            if reported > TODAY or reported < since:
                continue
            low, high = parse_range(_BRACKETS[int(rng.integers(len(_BRACKETS)))])
            trades.append(Trade("congress", member, role, ticker, BUY if rng.random() < 0.55 else SELL,
                                traded, reported, low, high))
        return trades

    def insider_trades(self, ticker: str, since: date) -> list[Trade]:
        if ticker not in _TICKERS or ticker in ("SPY", "QQQ"):
            return []
        rng = _rng("insider", ticker)
        trades = []
        for _ in range(int(rng.integers(0, 5))):
            name, title = _INSIDERS[int(rng.integers(len(_INSIDERS)))]
            traded = TODAY - timedelta(days=int(rng.integers(1, 120)))
            reported = traded + timedelta(days=2)
            if reported < since or reported > TODAY:
                continue
            side = BUY if rng.random() < 0.3 else SELL
            shares = float(rng.integers(1_000, 60_000))
            price = float(rng.uniform(40, 500))
            trades.append(Trade("insider", f"{name} {ticker}", title, ticker, side, traded, reported,
                                shares * price, shares * price, shares, price,
                                planned=side == SELL and rng.random() < 0.6))
        return trades

    def fund_report(self, fund: Fund) -> FundReport | None:
        rng = _rng("fund", fund.key)
        names = list(_TICKERS.items())[:14]
        prev, now = [], []
        for ticker, issuer in names:
            if rng.random() < 0.45:
                continue
            cusip = f"FX{zlib.crc32(ticker.encode()) % 10**7:07d}"
            shares = float(rng.integers(100_000, 50_000_000))
            price = float(rng.uniform(50, 400))
            roll = rng.random()
            if roll < 0.15:  # exited
                prev.append(Holding(issuer, cusip, shares * price, shares, ticker=ticker))
            elif roll < 0.30:  # new
                now.append(Holding(issuer, cusip, shares * price, shares, ticker=ticker))
            else:
                factor = float(rng.choice([0.6, 1.0, 1.0, 1.3]))
                prev.append(Holding(issuer, cusip, shares * price, shares, ticker=ticker))
                now.append(Holding(issuer, cusip, shares * factor * price * 1.05, shares * factor,
                                   ticker=ticker))
        return FundReport(
            fund=fund,
            period_now=date(2026, 6, 30),
            period_prev=date(2026, 3, 31),
            filed_now=date(2026, 8, 14),
            total_value=sum(h.value for h in now),
            changes=diff_holdings(now, prev),
        )

    def search_names(self, text: str, limit: int = 15) -> list[tuple[str, str]]:
        from .live import search_ticker_map

        return search_ticker_map({t: (0, n) for t, n in _TICKERS.items()}, text, limit)

    def all_names(self) -> list[tuple[str, str]]:
        return sorted(_TICKERS.items())
