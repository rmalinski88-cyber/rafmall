"""TradingView provider: the public screener endpoint, no login.

TradingView publishes no official data API, but the JSON endpoint that feeds
its web screener is public and login-free.  One POST with an explicit symbol
list returns fundamentals *and* the technical indicators TradingView already
computes (SMA, RSI, MACD, performance, 52-week range, volumes) for every
symbol at once - the whole universe in one request instead of forty, with
one consistent vocabulary across Tokyo, Seoul, Taipei, Hong Kong and the
mainland boards.

What it cannot give is price history, so ``get_prices`` is empty and the
technical score comes from ``get_technicals`` instead; the HTML report then
has no sparklines and says so.

It is unofficial.  Field names can change without notice, so a request
whose field the endpoint rejects is retried without that field and the
omission is reported through ``diagnostics()`` rather than hidden.  Treat
an empty answer as "source unavailable", never as "nothing matches".
"""

from __future__ import annotations

import hashlib
import json
import re

import pandas as pd

from .base import PRICE_COLUMNS, DataProvider, ProviderError

SCAN_URL = "https://scanner.tradingview.com/global/scan"
CHUNK_SIZE = 150

# Yahoo-style suffix -> TradingView exchange code.
_SUFFIX_EXCHANGE = {
    ".T": "TSE",
    ".KS": "KRX",
    ".KQ": "KRX",
    ".TW": "TWSE",
    ".TWO": "TPEX",
    ".HK": "HKEX",
    ".SS": "SSE",
    ".SZ": "SZSE",
    ".DE": "XETR",
    ".F": "FWB",
    ".PA": "EURONEXT",
    ".AS": "EURONEXT",
    ".SW": "SIX",
    ".ST": "OMXSTO",
    ".L": "LSE",
    ".MI": "MIL",
    ".WA": "GPW",
}

# Share-class separator: Yahoo writes SKF-B.ST, TradingView OMXSTO:SKF_B.
_CLASS_UNDERSCORE = {"OMXSTO"}

# Benchmark indices as the config names them (Yahoo symbols) -> TradingView
# candidates, tried in order.  The screener answers only for symbols it
# knows, so an index with an uncertain name gets several spellings and the
# first one that comes back wins.  (TWSE:TAIEX returned nothing on the first
# real run, 14 Oct 2026.)
_INDEX_CANDIDATES = {
    "^N225": ["TVC:NI225"],
    "^KS11": ["KRX:KOSPI"],
    "^KQ11": ["KRX:KOSDAQ"],
    "^TWII": ["TWSE:TAIEX", "TVC:TAIEX", "TWSE:IX0001", "TVC:TWII"],
    "^HSI": ["HSI:HSI"],
    "000001.SS": ["SSE:000001"],
    "399001.SZ": ["SZSE:399001"],
}
_INDEX_SYMBOLS = {name: candidates[0] for name, candidates in _INDEX_CANDIDATES.items()}

# Exchanges whose tickers TradingView writes without leading zeros.
_STRIP_ZEROS = {"HKEX"}

IDENTITY_COLUMNS = [
    "description", "sector", "industry", "currency", "fundamental_currency_code", "type",
]

# (canonical key, TradingView column, "pct" when TradingView reports a percentage)
FUNDAMENTAL_COLUMNS = [
    ("market_cap", "market_cap_basic", "raw"),
    ("total_revenue", "total_revenue_ttm", "raw"),
    ("revenue_growth", "total_revenue_yoy_growth_ttm", "pct"),
    ("earnings_growth", "net_income_yoy_growth_ttm", "pct"),
    ("gross_margin", "gross_margin_ttm", "pct"),
    ("operating_margin", "operating_margin_ttm", "pct"),
    ("profit_margin", "net_margin_ttm", "pct"),
    ("return_on_equity", "return_on_equity", "pct"),
    ("return_on_assets", "return_on_assets", "pct"),
    ("debt_to_equity", "debt_to_equity_fq", "raw"),
    ("current_ratio", "current_ratio_fq", "raw"),
    ("total_cash", "cash_n_short_term_invest_fq", "raw"),
    ("total_debt", "total_debt_fq", "raw"),
    ("free_cashflow", "free_cash_flow_ttm", "raw"),
    ("operating_cashflow", "cash_f_operating_activities_ttm", "raw"),
    ("trailing_pe", "price_earnings_ttm", "raw"),
    ("price_to_sales", "price_sales_current", "raw"),
    ("price_to_book", "price_book_fq", "raw"),
    ("ev_to_ebitda", "enterprise_value_ebitda_ttm", "raw"),
]

# Money amounts - market cap included - arrive in `fundamental_currency_code`,
# which on the global scan is USD even for Tokyo, Seoul and Hong Kong
# listings (verified on raw rows, 14 Oct 2026: Samsung cash 1.2e11, UBTech
# reporting currency 'USD'); prices and SMAs stay in the listing currency.
# Everything is brought into the listing currency so the pipeline's single
# listing-currency FX conversion is correct.
_MONEY_FIELDS = (
    "market_cap", "total_revenue", "total_cash", "total_debt", "free_cashflow", "operating_cashflow",
)

TECHNICAL_COLUMNS = [
    "close", "volume", "SMA50", "SMA200", "RSI", "MACD.macd", "MACD.signal",
    "Perf.1M", "Perf.3M", "Perf.6M", "Perf.Y",
    "price_52_week_high", "price_52_week_low",
    "average_volume_30d_calc", "average_volume_90d_calc", "ATR",
]

ALL_COLUMNS = (
    IDENTITY_COLUMNS
    + [column for _, column, _ in FUNDAMENTAL_COLUMNS]
    + TECHNICAL_COLUMNS
)


def to_tradingview(ticker: str) -> str:
    """``6324.T`` -> ``TSE:6324``; ``0020.HK`` -> ``HKEX:20``; ``^N225`` -> ``TVC:NI225``.

    A ticker already written as ``EXCHANGE:SYMBOL`` passes through, so a
    universe file may mix both spellings.
    """
    ticker = (ticker or "").strip()
    if ticker in _INDEX_SYMBOLS:
        return _INDEX_SYMBOLS[ticker]
    if ":" in ticker:
        return ticker.upper()
    upper = ticker.upper()
    for suffix in sorted(_SUFFIX_EXCHANGE, key=len, reverse=True):
        if upper.endswith(suffix):
            exchange = _SUFFIX_EXCHANGE[suffix]
            symbol = upper[: -len(suffix)]
            if exchange in _STRIP_ZEROS:
                symbol = symbol.lstrip("0") or "0"
            if exchange in _CLASS_UNDERSCORE:
                symbol = symbol.replace("-", "_")
            return f"{exchange}:{symbol}"
    return upper


def tradingview_url(ticker: str, exchange: str = "") -> str:
    """Chart link for a ticker: ``6324.T`` -> ``...?symbol=TSE%3A6324``.

    A US ticker without a known exchange goes in bare (``NVDA``) and
    TradingView resolves it; Yahoo's class separator becomes a dot
    (``BRK-B`` -> ``BRK.B``).
    """
    from urllib.parse import quote

    symbol = to_tradingview(ticker)
    if ":" not in symbol:
        symbol = symbol.replace("-", ".")
        if exchange:
            symbol = f"{exchange.upper()}:{symbol}"
    return "https://www.tradingview.com/chart/?symbol=" + quote(symbol, safe="")


def fx_symbol(currency: str) -> str:
    return f"FX_IDC:USD{currency.upper()}"


def _requests_transport(url: str, payload: dict, timeout: float) -> tuple[int, object]:
    """``(status, body)``; body is parsed JSON when possible, else text."""
    import requests

    response = requests.post(
        url,
        json=payload,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/",
        },
    )
    try:
        body: object = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


class TradingViewProvider(DataProvider):
    name = "tradingview"

    def __init__(self, cache=None, transport=None, timeout: float = 30.0):
        self.cache = cache
        self.transport = transport or _requests_transport
        self.timeout = timeout
        self._rows: dict[str, dict] = {}
        self._requested: set[str] = set()
        self._fx: dict[str, float | None] = {"USD": 1.0}
        self.dropped_columns: list[str] = []
        self._notes: list[str] = []

    # -- bulk fetch ----------------------------------------------------

    def prefetch(self, tickers: list[str]) -> None:
        symbols: list[str] = []
        for ticker in tickers:
            if not ticker:
                continue
            symbols.extend(_INDEX_CANDIDATES.get(ticker, [to_tradingview(ticker)]))
        self._fetch_symbols(symbols)

        currencies: set[str] = set()
        for row in self._rows.values():
            for key in ("currency", "fundamental_currency_code"):
                if row.get(key):
                    currencies.add(str(row[key]).upper())
        self._fetch_fx(sorted(c for c in currencies if c not in self._fx))

    def _fetch_symbols(self, symbols: list[str]) -> None:
        pending = [s for s in dict.fromkeys(symbols) if s not in self._requested]
        if not pending:
            return
        self._requested.update(pending)
        for start in range(0, len(pending), CHUNK_SIZE):
            chunk = pending[start : start + CHUNK_SIZE]
            self._rows.update(self._scan(chunk, ALL_COLUMNS))
        # An index counts as missing only when none of its spellings answered;
        # a failed alternate spelling is expected, not news.
        index_symbols = {c for cands in _INDEX_CANDIDATES.values() for c in cands}
        missing = [s for s in pending if s not in index_symbols and s not in self._rows]
        for cands in _INDEX_CANDIDATES.values():
            if any(c in pending for c in cands) and not any(c in self._rows for c in cands):
                missing.append(" / ".join(cands))
        if missing:
            self._notes.append(
                f"TradingView nie zwrócił danych dla: {', '.join(missing)}"
            )

    def _fetch_fx(self, currencies: list[str]) -> None:
        if not currencies:
            return
        rows = self._scan([fx_symbol(c) for c in currencies], ["close"])
        for currency in currencies:
            close = rows.get(fx_symbol(currency), {}).get("close")
            try:
                per_usd = float(close) if close is not None else None
            except (TypeError, ValueError):
                per_usd = None
            self._fx[currency] = (1.0 / per_usd) if per_usd else None
            if not per_usd:
                self._notes.append(f"brak kursu {currency}/USD w TradingView")

    def _scan(self, symbols: list[str], columns: list[str]) -> dict[str, dict]:
        """One screener request, retried without any field the endpoint rejects."""
        key = hashlib.sha1(json.dumps([sorted(symbols), columns]).encode()).hexdigest()
        if self.cache is not None:
            cached = self.cache.get_json("tradingview", key)
            if cached is not None:
                self._absorb_dropped(cached.get("dropped", []))
                return cached.get("rows", {})

        wanted = list(columns)
        for _attempt in range(len(wanted)):
            payload = {"symbols": {"tickers": symbols, "query": {"types": []}}, "columns": wanted}
            status, body = self.transport(SCAN_URL, payload, self.timeout)

            if status == 200 and isinstance(body, dict):
                rows = _parse(body, wanted)
                if self.cache is not None:
                    self.cache.put_json(
                        "tradingview", key, {"rows": rows, "dropped": self._dropped_from(columns, wanted)}
                    )
                return rows

            text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
            rejected = [c for c in wanted if _mentions(text, c)]
            if status in (400, 422) and rejected:
                self._absorb_dropped(rejected)
                wanted = [c for c in wanted if c not in rejected]
                if not wanted:
                    break
                continue
            raise ProviderError(f"TradingView scanner: HTTP {status}: {text[:300]}")

        raise ProviderError("TradingView scanner odrzucił każde pole zapytania")

    def _dropped_from(self, requested: list[str], kept: list[str]) -> list[str]:
        return [c for c in requested if c not in kept]

    def _absorb_dropped(self, columns: list[str]) -> None:
        for column in columns:
            if column not in self.dropped_columns:
                self.dropped_columns.append(column)

    def scan_columns(self, candidates: dict[str, list[str]], columns: list[str]) -> dict[str, dict]:
        """``key -> row`` for arbitrary screener columns; rejected columns are dropped and noted.

        ``candidates`` maps a caller's key to TradingView symbols to try
        (``{"NVDA": ["NASDAQ:NVDA", "NYSE:NVDA"]}``); the first that answers wins.
        """
        pending = list(dict.fromkeys(sym for syms in candidates.values() for sym in syms))
        rows: dict[str, dict] = {}
        for start in range(0, len(pending), CHUNK_SIZE):
            rows.update(self._scan(pending[start : start + CHUNK_SIZE], columns))
        out = {}
        for key, symbols in candidates.items():
            hit = next((rows[s] for s in symbols if s in rows), None)
            if hit is not None:
                out[key] = hit
        return out

    def raw_row(self, ticker: str) -> dict | None:
        """The screener's row exactly as received - for diagnosing units."""
        row = self._row(ticker)
        return dict(row) if row else None

    def _row(self, ticker: str) -> dict | None:
        candidates = _INDEX_CANDIDATES.get(ticker, [to_tradingview(ticker)])
        if any(c not in self._requested for c in candidates):
            self.prefetch([ticker])  # also picks up FX for a currency seen for the first time
        for symbol in candidates:
            if symbol in self._rows:
                return self._rows[symbol]
        return None

    # -- DataProvider --------------------------------------------------

    def get_prices(self, ticker: str, lookback_days: int) -> pd.DataFrame:
        # The screener has no history; technicals come from get_technicals.
        return pd.DataFrame(columns=PRICE_COLUMNS)

    def get_fundamentals(self, ticker: str) -> dict:
        row = self._row(ticker)
        if not row:
            return {}

        listing = (row.get("currency") or "").upper() or None
        reporting = (row.get("fundamental_currency_code") or listing or "").upper() or None

        out: dict = {
            "name": row.get("description"),
            "sector": row.get("sector"),
            "industry": row.get("industry"),
            "currency": listing,
            "quote_type": row.get("type"),
        }
        for canonical, column, kind in FUNDAMENTAL_COLUMNS:
            value = _number(row.get(column))
            if value is not None and kind == "pct":
                value = value / 100.0
            out[canonical] = value

        # Money amounts arrive in the reporting currency; bring them into the
        # listing currency so ratios and the pipeline's FX step stay honest.
        if listing and reporting and reporting != listing:
            factor = self._cross_rate(reporting, listing)
            for field in _MONEY_FIELDS:
                if out.get(field) is not None:
                    out[field] = out[field] * factor if factor else None
            if factor is None:
                self._note_once(
                    f"{ticker}: sprawozdania w {reporting}, notowanie w {listing}, "
                    f"brak kursu do przeliczenia - kwoty pominięte"
                )
        return out

    def get_technicals(self, ticker: str) -> dict | None:
        row = self._row(ticker)
        if not row:
            return None

        close = _number(row.get("close"))
        if close is None or close <= 0:
            return None

        sma50, sma200 = _number(row.get("SMA50")), _number(row.get("SMA200"))
        macd, signal = _number(row.get("MACD.macd")), _number(row.get("MACD.signal"))
        high, low = _number(row.get("price_52_week_high")), _number(row.get("price_52_week_low"))
        vol30, vol90 = _number(row.get("average_volume_30d_calc")), _number(row.get("average_volume_90d_calc"))
        atr = _number(row.get("ATR"))

        out: dict = {
            "last_close": close,
            "bars": None,
            "sma50": sma50,
            "sma200": sma200,
            "px_vs_sma50": _ratio(close, sma50),
            "px_vs_sma200": _ratio(close, sma200),
            "sma50_vs_sma200": _ratio(sma50, sma200),
            "rsi14": _number(row.get("RSI")),
            "macd_hist_pct": ((macd - signal) / close) if (macd is not None and signal is not None) else None,
            "ret_1m": _pct(row.get("Perf.1M")),
            "ret_3m": _pct(row.get("Perf.3M")),
            "ret_6m": _pct(row.get("Perf.6M")),
            "ret_12m": _pct(row.get("Perf.Y")),
            "high_52w": high,
            "low_52w": low,
            "dist_52w_high": _ratio(close, high),
            "pos_52w_range": ((close - low) / (high - low)) if (high is not None and low is not None and high > low) else None,
            "max_drawdown_12m": None,
            "atr_pct": (atr / close) if atr is not None else None,
            "avg_volume_20d": vol30,
            "volume_trend": _ratio(vol30, vol90),
            "avg_turnover_local": (vol30 * close) if vol30 is not None else None,
        }
        return out

    def get_fx_to_usd(self, currency: str) -> float | None:
        currency = (currency or "").upper()
        if not currency:
            return None
        if currency not in self._fx:
            self._fetch_fx([currency])
        return self._fx.get(currency)

    def diagnostics(self) -> list[str]:
        notes = list(self._notes)
        if self.dropped_columns:
            notes.insert(
                0,
                "TradingView odrzucił pola (pominięte w tym przebiegu): "
                + ", ".join(self.dropped_columns),
            )
        empty = self._all_null_columns()
        if empty:
            notes.append(
                "pola bez żadnej wartości u TradingView (sprawdź nazwy): " + ", ".join(empty)
            )
        return notes

    def _all_null_columns(self) -> list[str]:
        if not self._rows:
            return []
        stock_rows = [r for r in self._rows.values() if r.get("type") in (None, "stock", "dr")]
        if not stock_rows:
            return []
        return [
            column
            for column in ALL_COLUMNS
            if column not in self.dropped_columns
            and all(r.get(column) is None for r in stock_rows)
        ]

    def _cross_rate(self, from_currency: str, to_currency: str) -> float | None:
        """Units of ``to_currency`` per one unit of ``from_currency``."""
        a, b = self.get_fx_to_usd(from_currency), self.get_fx_to_usd(to_currency)
        return (a / b) if (a and b) else None

    def _note_once(self, note: str) -> None:
        if note not in self._notes:
            self._notes.append(note)


# -- helpers --------------------------------------------------------------


def _parse(body: dict, columns: list[str]) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for item in body.get("data", []) or []:
        symbol = item.get("s")
        values = item.get("d") or []
        if not symbol or len(values) != len(columns):
            continue
        rows[str(symbol)] = dict(zip(columns, values))
    return rows


def _mentions(text: str, column: str) -> bool:
    """Whether an error message names this column (whole token, not substring)."""
    return re.search(r"(?<![\w.])" + re.escape(column) + r"(?![\w.])", text) is not None


def _number(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and number not in (float("inf"), float("-inf")) else None


def _pct(value) -> float | None:
    number = _number(value)
    return (number / 100.0) if number is not None else None


def _ratio(numerator, denominator) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return float(numerator) / float(denominator) - 1.0
