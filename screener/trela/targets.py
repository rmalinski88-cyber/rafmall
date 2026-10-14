"""Second source of analyst price targets: TradingView, plus a history we keep ourselves.

Yahoo has per-firm target history (``upgrades_downgrades``) only for US
listings; for Tokyo, Seoul, Taipei and Hong Kong it is empty, so Trela's
value rules (41 of 129 points) had no reading there.  TradingView's public
screener publishes the *current* analyst consensus for those exchanges, free
and without login, but no history.  So every run - and a daily snapshot job -
stores the consensus, and the history grows:

* from day one: the current upside ("nie kupuj teraz" works for Asia);
* after ~45 days: the 45-day target drawdown (must-have);
* after ~180 days: the 180-day target change;
* after ~2 years: the upside channel.

The column names come from TradingView's screener and are unofficial; a
column the endpoint rejects is dropped and named in ``diagnostics()``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import Readings, channel_position, pt_change, pt_max_drawdown

# Tried in this order; the first non-empty one is the consensus.
TARGET_COLUMNS = ["price_target_average", "price_target_median", "price_target_1y"]
EXTRA_COLUMNS = ["close", "currency", "price_target_high", "price_target_low"]
US_EXCHANGES = ("NASDAQ", "NYSE", "AMEX")
PT_RULES = ("pt_change_180d", "pt_drawdown_45d", "upside_vs_history")


def symbol_candidates(ticker: str, exchange: str = "") -> list[str]:
    """TradingView symbols to try for a Yahoo ticker."""
    from ..providers.tradingview import to_tradingview

    symbol = to_tradingview(ticker)
    if ":" in symbol:
        return [symbol]
    symbol = symbol.replace("-", ".")
    if exchange:
        return [f"{exchange.upper()}:{symbol}"]
    return [f"{ex}:{symbol}" for ex in US_EXCHANGES]


class TargetHistory:
    """``date, ticker, target, close`` snapshots in one CSV (kept in the Actions cache)."""

    COLUMNS = ["date", "ticker", "target", "close", "source"]

    def __init__(self, path: str | Path):
        self.path = Path(path)
        try:
            frame = pd.read_csv(self.path, dtype={"ticker": str})
        except (OSError, ValueError):
            frame = pd.DataFrame(columns=self.COLUMNS)
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        self.frame = frame.dropna(subset=["date"])

    def record(self, day, values: dict[str, tuple[float, float | None]], source: str = "tradingview") -> None:
        """Store ``ticker -> (target, close)`` for ``day``; a re-run on the same day replaces it."""
        day = pd.Timestamp(day).normalize()
        new = pd.DataFrame(
            [{"date": day, "ticker": t, "target": v[0], "close": v[1], "source": source}
             for t, v in values.items() if v[0]],
            columns=self.COLUMNS,
        )
        if new.empty:
            return
        keep = ~((self.frame["date"] == day) & self.frame["ticker"].isin(new["ticker"]))
        self.frame = pd.concat([self.frame[keep], new], ignore_index=True).sort_values(["ticker", "date"])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        out = self.frame.copy()
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
        out.to_csv(self.path, index=False)

    def series(self, ticker: str, column: str = "target") -> pd.Series:
        rows = self.frame[self.frame["ticker"] == ticker]
        return pd.Series(pd.to_numeric(rows[column], errors="coerce").to_numpy(),
                         index=pd.DatetimeIndex(rows["date"])).dropna()


class TradingViewTargets:
    """Fetch today's consensus for a universe and fill the readings Yahoo left empty."""

    def __init__(self, history: TargetHistory, provider=None, today=None):
        from ..providers.tradingview import TradingViewProvider

        self.history = history
        self.provider = provider or TradingViewProvider()
        self.today = pd.Timestamp(today or pd.Timestamp.today()).normalize()
        self.snapshot: dict[str, dict] = {}
        self.notes: list[str] = []

    def prefetch(self, tickers, exchanges: dict | None = None) -> int:
        """One screener request per 150 symbols; returns how many came back with a target."""
        exchanges = exchanges or {}
        candidates = {t: symbol_candidates(t, exchanges.get(t) or "") for t in tickers if t}
        try:
            rows = self.provider.scan_columns(candidates, EXTRA_COLUMNS + TARGET_COLUMNS)
        except Exception as exc:  # noqa: BLE001 - unofficial endpoint: report, do not stop the run
            self.notes.append(f"TradingView (cele analityków) niedostępny: {exc}")
            return 0
        for ticker, row in rows.items():
            target = next((_number(row.get(c)) for c in TARGET_COLUMNS if _number(row.get(c))), None)
            if target:
                self.snapshot[ticker] = {"target": target, "close": _number(row.get("close")),
                                         "high": _number(row.get("price_target_high")),
                                         "low": _number(row.get("price_target_low"))}
        self.history.record(self.today, {t: (v["target"], v["close"]) for t, v in self.snapshot.items()})
        dropped = [c for c in self.provider.dropped_columns if c in TARGET_COLUMNS + EXTRA_COLUMNS]
        if dropped:
            self.notes.append("TradingView odrzucił pola: " + ", ".join(dropped))
        return len(self.snapshot)

    def fill(self, r: Readings) -> Readings:
        """Fill price-target readings Yahoo did not provide (Asian listings, some US)."""
        if r.prefiltr or r.empty or any(r.values.get(rule) is not None for rule in PT_RULES):
            return r
        snap = self.snapshot.get(r.ticker)
        series = self.history.series(r.ticker)
        if snap is None and series.empty:
            return r

        if snap and snap.get("close"):
            r.price_target = snap["target"]
            r.upside_now = snap["target"] / snap["close"] - 1.0
        r.values["pt_change_180d"] = pt_change(series, 180)
        r.values["pt_drawdown_45d"] = pt_max_drawdown(series, 45)
        r.values["upside_vs_history"] = _upside_position(self.history, r.ticker, r.upside_now)
        if not series.empty:
            days = (series.index[-1] - series.index[0]).days
            r.notes.append(f"cele analityków: TradingView, historia {days} dni od {series.index[0]:%d.%m.%Y}"
                           + (" — zmiana 180 dni i kanał upside jeszcze bez danych" if days < 180 else ""))
        return r


def _upside_position(history: TargetHistory, ticker: str, current: float | None) -> float | None:
    """Current upside within its own monthly history, as for Yahoo-sourced companies."""
    target, close = history.series(ticker, "target"), history.series(ticker, "close")
    if target.empty or close.empty:
        return None
    monthly = (target / close - 1.0).dropna().resample("ME").last().dropna()
    return channel_position(current, monthly)


def _number(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number else None
