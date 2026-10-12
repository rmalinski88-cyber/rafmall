"""Live feed: SEC EDGAR for insiders and 13F, Quiver for Congress."""

from __future__ import annotations

import os
from datetime import date

from ..funds import build_name_index, diff_holdings, load_cusip_map, resolve_tickers
from ..models import Fund, FundReport, Trade
from .base import TradeFeed
from .quiver import QuiverClient, parse_congress_rows
from .sec import SecClient


class LiveFeed(TradeFeed):
    name = "live"

    def __init__(self, config: dict, fresh_cache=None, archive_cache=None):
        super().__init__()
        self.config = config
        self._caches = (fresh_cache, archive_cache)
        self._sec: SecClient | None = None
        self._sec_error: str | None = None

        api_key = os.environ.get("QUIVER_API_KEY") or config.get("quiver_api_key") or ""
        self.quiver = QuiverClient(api_key, cache=fresh_cache) if api_key else None
        self._name_index: dict[str, str] | None = None

    @property
    def sec(self) -> SecClient:
        """Built on first use; raises FeedError when SEC_USER_AGENT is missing."""
        if self._sec is None:
            user_agent = os.environ.get("SEC_USER_AGENT") or self.config.get("sec_user_agent") or ""
            self._sec = SecClient(user_agent, fresh_cache=self._caches[0], archive_cache=self._caches[1])
        return self._sec

    def sec_ready(self) -> bool:
        """True when SEC can be used; otherwise warns once and returns False."""
        if self._sec_error is not None:
            return False
        try:
            self.sec
            return True
        except Exception as exc:  # FeedError: no User-Agent
            self._sec_error = str(exc)
            self.warn(f"SEC pominięte: {exc}")
            return False

    def congress_trades(self, since: date) -> list[Trade]:
        if self.quiver is None:
            self.warn("Brak QUIVER_API_KEY — transakcje Kongresu pominięte. "
                      "Ustaw klucz API Quiver Quantitative, żeby je włączyć.")
            return []
        try:
            rows = self.quiver.congress_rows()
        except Exception as exc:
            self.warn(f"Quiver: nie udało się pobrać transakcji Kongresu ({exc}).")
            return []
        trades, skipped = parse_congress_rows(rows, since=since)
        if skipped:
            self.warn(f"Quiver: pominięto {skipped} wierszy (wymiany, brak tickera lub nieznany format).")
        return trades

    def insider_trades(self, ticker: str, since: date) -> list[Trade]:
        if not self.sec_ready():
            return []
        try:
            return self.sec.insider_trades(
                ticker, since, max_filings=int(self.config.get("insider_max_filings", 40))
            )
        except Exception as exc:
            self.warn(f"SEC Form 4 dla {ticker}: {exc}")
            return []

    def fund_report(self, fund: Fund) -> FundReport | None:
        if not self.sec_ready():
            return None
        try:
            filings = self.sec.latest_13f(fund.cik, count=2)
        except Exception as exc:
            self.warn(f"SEC 13F dla {fund.name}: {exc}")
            return None
        if not filings or not filings[0][1]:
            self.warn(f"{fund.name}: brak czytelnego zgłoszenia 13F-HR (CIK {fund.cik}).")
            return None

        cusip_map = load_cusip_map(self.config.get("cusip_map", "data/cusip_tickers.csv"))
        index = self._names()
        now_filing, now = filings[0]
        prev_filing, prev = filings[1] if len(filings) > 1 else ({}, [])
        now = resolve_tickers(now, cusip_map, index)
        prev = resolve_tickers(prev, cusip_map, index)

        return FundReport(
            fund=fund,
            period_now=now_filing.get("period"),
            period_prev=prev_filing.get("period"),
            filed_now=now_filing.get("filed"),
            total_value=sum(h.value for h in now),
            changes=diff_holdings(now, prev, float(self.config.get("fund_min_change", 0.05))),
        )

    def search_names(self, text: str, limit: int = 15) -> list[tuple[str, str]]:
        if not self.sec_ready():
            return []
        return search_ticker_map(self.sec.tickers(), text, limit)

    def all_names(self) -> list[tuple[str, str]]:
        """Every SEC registrant as (ticker, name); [] when SEC is unavailable."""
        if not self.sec_ready():
            return []
        return [(t, title) for t, (_, title) in self.sec.tickers().items()]

    def _names(self) -> dict[str, str]:
        if self._name_index is None:
            try:
                self._name_index = build_name_index(self.sec.tickers())
            except Exception as exc:
                self.warn(f"SEC: nie udało się pobrać listy tickerów ({exc}); 13F bez tickerów.")
                self._name_index = {}
        return self._name_index


def search_ticker_map(tickers: dict[str, tuple[int, str]], text: str, limit: int) -> list[tuple[str, str]]:
    """Exact ticker first, then ticker prefixes, then name substrings."""
    needle = text.strip().upper()
    if not needle:
        return []
    exact, prefix, named = [], [], []
    for ticker, (_, title) in tickers.items():
        if ticker == needle:
            exact.append((ticker, title))
        elif ticker.startswith(needle):
            prefix.append((ticker, title))
        elif needle in title.upper():
            named.append((ticker, title))
    return (exact + sorted(prefix) + named)[:limit]
