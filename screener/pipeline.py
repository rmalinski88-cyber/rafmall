"""The screening pipeline: fetch -> derive -> filter -> score -> rank."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from .analysis.fundamental import compute_fundamental_metrics
from .analysis.scoring import build_specs, score_universe
from .analysis.technical import compute_technical_metrics
from .config import benchmark_for, group_weights, resolve_profile
from .providers import DataProvider


@dataclass
class ScreenResult:
    """Everything a report needs from one run."""

    ranked: pd.DataFrame              # passing companies, best first
    rejected: pd.DataFrame            # excluded companies + the reason
    prices: dict = field(default_factory=dict)   # ticker -> close series (for sparklines)
    profile_name: str = ""
    provider_name: str = ""
    run_date: str = field(default_factory=lambda: date.today().isoformat())
    warnings: list = field(default_factory=list)

    @property
    def screened_count(self) -> int:
        return len(self.ranked) + len(self.rejected)


def run_screen(
    universe: pd.DataFrame,
    provider: DataProvider,
    config: dict,
    profile_name: str | None = None,
    progress=None,
) -> ScreenResult:
    """Screen every ticker in ``universe`` and return a ranked result.

    ``progress`` is an optional ``callable(index, total, ticker)`` used by the
    CLI to print a progress line; the pipeline itself prints nothing.
    """
    profile_name, profile = resolve_profile(config, profile_name)
    specs = build_specs(profile)
    weights = group_weights(profile)
    lookback = int(config.get("lookback_days", 420))
    filters = config.get("filters") or {}

    tickers = [t for t in universe["ticker"] if t]
    benchmark_symbols = sorted({s for s in (benchmark_for(t, config) for t in tickers) if s})
    # A bulk provider answers for everything in one request; others ignore this.
    provider.prefetch([*tickers, *benchmark_symbols])

    benchmarks = _load_benchmarks(universe, provider, config, lookback)

    rows, prices, warnings = [], {}, []
    total = len(universe)

    for position, entry in enumerate(universe.to_dict("records"), start=1):
        ticker = entry["ticker"]
        if progress:
            progress(position, total, ticker)

        row = {
            "ticker": ticker,
            "name": entry.get("name") or ticker,
            "market": entry.get("market", ""),
            "segment": entry.get("segment", ""),
            "confidence": entry.get("confidence", ""),
            "notes": entry.get("notes", ""),
        }

        price_frame = provider.get_prices(ticker, lookback)
        has_prices = price_frame is not None and not price_frame.empty
        technicals = None if has_prices else provider.get_technicals(ticker)

        if not has_prices and not technicals:
            row["excluded_reason"] = "brak danych cenowych"
            rows.append(row)
            warnings.append(f"{ticker}: brak notowań u dostawcy")
            continue

        benchmark_symbol = benchmark_for(ticker, config)
        row["benchmark"] = benchmark_symbol
        if has_prices:
            prices[ticker] = price_frame["close"]
            row.update(compute_technical_metrics(price_frame, benchmarks.get(benchmark_symbol)))
        else:
            # Source-computed indicators; relative strength from the index's
            # own performance figures, since there is no history to align.
            row.update(technicals)
            index = provider.get_technicals(benchmark_symbol) if benchmark_symbol else None
            row.update(relative_strength_from_metrics(technicals, index))

        fundamentals = compute_fundamental_metrics(provider.get_fundamentals(ticker))
        # The universe file is the authority on the display name.
        fundamentals.pop("name", None)
        row.update(fundamentals)

        rows.append(row)

    frame = pd.DataFrame(rows).set_index("ticker", drop=False)
    frame = _add_usd_columns(frame, provider, warnings)
    frame = _apply_filters(frame, filters)
    warnings.extend(provider.diagnostics())

    passing = frame[frame["excluded_reason"].isna()].copy()
    rejected = frame[frame["excluded_reason"].notna()].copy()

    # First scoring pass establishes fundamental coverage; names that report
    # too little are then dropped and the ranks recomputed without them, so a
    # thin-data company neither gets a score nor distorts anyone else's.
    if passing.empty:
        ranked = score_universe(passing, specs, weights)
    else:
        scored = score_universe(passing, specs, weights)
        min_coverage = filters.get("min_fundamental_coverage")

        if min_coverage is not None:
            thin = scored["fundamental_coverage"].fillna(0.0) < float(min_coverage)
            if thin.any():
                dropped = scored[thin].copy()
                dropped["excluded_reason"] = dropped["fundamental_coverage"].map(
                    lambda c: f"za mało danych fundamentalnych ({c:.0%})"
                )
                rejected = pd.concat([rejected, dropped[frame.columns]])
                passing = passing[~thin]
                # Re-score without them so the dropped names no longer
                # influence anyone else's percentile.  An empty survivor set
                # still has to keep the score columns for the report.
                scored = (
                    score_universe(passing, specs, weights)
                    if not passing.empty
                    else scored.iloc[0:0]
                )

        ranked = scored.sort_values("composite_score", ascending=False, na_position="last")

    return ScreenResult(
        ranked=ranked,
        rejected=rejected,
        prices=prices,
        profile_name=profile_name,
        provider_name=getattr(provider, "name", "?"),
        warnings=warnings,
    )


def _load_benchmarks(
    universe: pd.DataFrame, provider: DataProvider, config: dict, lookback: int
) -> dict:
    """Fetch each distinct benchmark index once, not once per ticker."""
    symbols = {benchmark_for(t, config) for t in universe["ticker"]}
    out = {}
    for symbol in filter(None, symbols):
        frame = provider.get_prices(symbol, lookback)
        out[symbol] = frame["close"] if frame is not None and not frame.empty else None
    return out


def relative_strength_from_metrics(stock: dict, index: dict | None) -> dict:
    """``rs_3m`` / ``rs_6m`` as stock return minus index return, when both exist."""
    out = {"rs_3m": None, "rs_6m": None}
    if not index:
        return out
    for label in ("3m", "6m"):
        a, b = stock.get(f"ret_{label}"), index.get(f"ret_{label}")
        if a is not None and b is not None:
            out[f"rs_{label}"] = float(a) - float(b)
    return out


def _add_usd_columns(frame: pd.DataFrame, provider: DataProvider, warnings: list) -> pd.DataFrame:
    """Convert market cap and turnover to USD so filters compare like with like."""
    if frame.empty:
        frame["market_cap_usd"] = pd.Series(dtype=float)
        frame["avg_turnover_usd"] = pd.Series(dtype=float)
        return frame

    rates: dict[str, float | None] = {}
    for currency in frame.get("currency", pd.Series(dtype=str)).dropna().unique():
        rate = provider.get_fx_to_usd(currency)
        rates[currency] = rate
        if rate is None:
            warnings.append(f"brak kursu {currency}/USD - filtry walutowe pominięte dla tych spółek")

    fx = frame["currency"].map(rates) if "currency" in frame else None
    frame["fx_to_usd"] = fx
    frame["market_cap_usd"] = frame.get("market_cap") * fx if fx is not None else None
    frame["avg_turnover_usd"] = frame.get("avg_turnover_local") * fx if fx is not None else None
    return frame


def _apply_filters(frame: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Set ``excluded_reason`` on every row failing a hard gate.

    A missing value never fails a filter - absent data is a coverage problem,
    reported separately, not evidence that a company is too small or too
    indebted.
    """
    frame = frame.copy()
    if "excluded_reason" not in frame.columns:
        frame["excluded_reason"] = pd.NA

    def reject(mask: pd.Series, reason: str) -> None:
        target = mask.fillna(False) & frame["excluded_reason"].isna()
        frame.loc[target, "excluded_reason"] = reason

    min_bars = filters.get("min_price_bars")
    if min_bars is not None and "bars" in frame:
        reject(frame["bars"] < int(min_bars), f"za krótka historia (<{int(min_bars)} sesji)")

    min_cap = filters.get("min_market_cap_usd")
    if min_cap is not None and "market_cap_usd" in frame:
        reject(frame["market_cap_usd"] < float(min_cap), f"kapitalizacja < {_usd(min_cap)}")

    min_turnover = filters.get("min_avg_turnover_usd")
    if min_turnover is not None and "avg_turnover_usd" in frame:
        reject(
            frame["avg_turnover_usd"] < float(min_turnover),
            f"obrót dzienny < {_usd(min_turnover)}",
        )

    max_de = filters.get("max_debt_to_equity")
    if max_de is not None and "debt_to_equity" in frame:
        reject(frame["debt_to_equity"] > float(max_de), f"dług/kapitał > {float(max_de):.1f}")

    return frame


def _usd(value: float) -> str:
    """Threshold amounts for filter messages, in Polish number formatting."""
    value = float(value)
    if value >= 1e9:
        return f"{value / 1e9:.1f} mld USD".replace(".", ",")
    if value >= 1e6:
        return f"{value / 1e6:.0f} mln USD"
    return f"{value:,.0f} USD".replace(",", " ")
