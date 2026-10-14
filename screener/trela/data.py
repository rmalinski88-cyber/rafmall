"""Readings for Trela's rules, computed from what Yahoo Finance returns.

Verified on real data (Actions task ``probe``, 14 Oct 2026):

* ``earnings_estimate`` / ``revenue_estimate``: rows ``0y`` and ``+1y`` with
  ``growth`` and ``numberOfAnalysts`` - present for US and Asian listings;
* ``growth_estimates`` row ``LTG``: usually empty, so the 5-year EPS rule
  often has no reading;
* ``upgrades_downgrades``: per-firm price targets (``currentPriceTarget``)
  going back years for US listings, empty for Tokyo / Seoul;
* annual statements: 4-5 fiscal years, so "change over 5 years" is
  extrapolated from the compound annual rate over the span there is;
* no CFO forecasts at all - that rule drops out of the maximum.

Every function below the fetch section is pure and tested offline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

YEARS_FOR_CHANGE = 5
PT_LOOKBACK_DAYS = 365        # a firm's target counts in the consensus for a year
UPSIDE_HISTORY_YEARS = 4
UPSIDE_CHANNEL = (0.15, 0.85)  # "kanał poziomy, ok. 70% odczytów w kanale"
MIN_UPSIDE_POINTS = 24         # months of history needed before the channel means anything


@dataclass
class Readings:
    ticker: str
    name: str = ""
    currency: str = ""
    values: dict = field(default_factory=dict)       # rule id -> reading
    notes: list = field(default_factory=list)        # how a reading was obtained / why missing
    years_since_ipo: float | None = None
    upside_now: float | None = None
    price_target: float | None = None
    humanoid: bool = False
    prefiltr: str = ""                              # why Trela's screener cut it; "" = passed


# -- pure computations ----------------------------------------------------------


def change_over_years(points: pd.Series, years: int = YEARS_FOR_CHANGE) -> tuple[float | None, float | None]:
    """``(equivalent change over `years`, actual span in years)`` from annual values.

    Values are indexed by period end.  The compound annual rate between the
    oldest and newest available values is projected onto ``years``.  A start
    at or below zero has no meaningful growth rate and yields ``None``.
    """
    series = pd.to_numeric(points, errors="coerce").dropna()
    if len(series) < 2:
        return None, None
    series = series.sort_index()
    start, end = float(series.iloc[0]), float(series.iloc[-1])
    span = (pd.Timestamp(series.index[-1]) - pd.Timestamp(series.index[0])).days / 365.25
    if span < 1.5 or start <= 0:
        return None, span
    if end <= 0:
        return -1.0, span
    annual = (end / start) ** (1.0 / span) - 1.0
    return (1.0 + annual) ** years - 1.0, span


def average_growth(first: float | None, second: float | None) -> float | None:
    """Average annual growth over two consecutive years (geometric)."""
    if first is None or second is None:
        return None
    try:
        a, b = 1.0 + float(first), 1.0 + float(second)
    except (TypeError, ValueError):
        return None
    if not all(map(math.isfinite, (a, b))) or a <= 0 or b <= 0:
        return None
    return math.sqrt(a * b) - 1.0


def altman_z_nonmanufacturing(working_capital, retained_earnings, ebit, equity,
                              total_assets, total_liabilities) -> float | None:
    """Altman Z''-Score for non-manufacturers (no constant term)."""
    values = [working_capital, retained_earnings, ebit, equity, total_assets, total_liabilities]
    if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in values):
        return None
    if total_assets <= 0 or total_liabilities <= 0:
        return None
    return (
        6.56 * working_capital / total_assets
        + 3.26 * retained_earnings / total_assets
        + 6.72 * ebit / total_assets
        + 1.05 * equity / total_liabilities
    )


def consensus_targets(actions: pd.DataFrame, dates, lookback_days: int = PT_LOOKBACK_DAYS) -> pd.Series:
    """Consensus price target on each date, rebuilt from per-firm target changes.

    On a given day, each firm's latest positive target from the preceding
    ``lookback_days`` counts once; the consensus is their mean.
    """
    dates = pd.DatetimeIndex(dates)
    if actions is None or actions.empty or "currentPriceTarget" not in actions.columns:
        return pd.Series(float("nan"), index=dates)

    frame = actions[["Firm", "currentPriceTarget"]].copy()
    frame.index = pd.DatetimeIndex(frame.index).tz_localize(None)
    frame = frame[pd.to_numeric(frame["currentPriceTarget"], errors="coerce") > 0].sort_index()

    out = []
    window = pd.Timedelta(days=lookback_days)
    for day in dates:
        recent = frame[(frame.index <= day) & (frame.index > day - window)]
        if recent.empty:
            out.append(float("nan"))
            continue
        latest = recent.groupby("Firm")["currentPriceTarget"].last()
        out.append(float(latest.astype(float).mean()))
    return pd.Series(out, index=dates)


def adjust_for_splits(actions: pd.DataFrame, splits: pd.Series | None) -> pd.DataFrame:
    """Targets restated in today's shares.

    Yahoo's closing prices are split-adjusted, its price targets are not:
    NVDA's targets before the 10:1 split of June 2024 are ten times today's
    scale, which would read as a 90% target cut and a huge historic upside.
    """
    if actions is None or actions.empty or splits is None or len(splits) == 0:
        return actions
    ratios = pd.to_numeric(splits, errors="coerce")
    ratios.index = pd.DatetimeIndex(ratios.index).tz_localize(None)
    ratios = ratios[ratios > 0]
    if ratios.empty:
        return actions
    out = actions.copy()
    when = pd.DatetimeIndex(out.index).tz_localize(None)
    factor = pd.Series(1.0, index=range(len(out)))
    for day, ratio in ratios.items():
        factor[when < day] *= float(ratio)
    out["currentPriceTarget"] = pd.to_numeric(out["currentPriceTarget"], errors="coerce") / factor.to_numpy()
    return out


def anchored_drawdown(actions: pd.DataFrame, today, days: int = 45,
                      lookback_days: int = PT_LOOKBACK_DAYS) -> float | None:
    """Worst fall of the consensus within ``days``, counting only real target cuts.

    The firm set is fixed at the start of the window: a high target that
    merely expires, or a new firm initiating low, changes the plain mean
    without any analyst cutting - Trela's rule is about cuts.
    """
    if actions is None or actions.empty or "currentPriceTarget" not in actions.columns:
        return None
    frame = actions[["Firm", "currentPriceTarget"]].copy()
    frame.index = pd.DatetimeIndex(frame.index).tz_localize(None)
    frame["currentPriceTarget"] = pd.to_numeric(frame["currentPriceTarget"], errors="coerce")
    frame = frame[frame["currentPriceTarget"] > 0].sort_index()

    today = pd.Timestamp(today)
    if today.tzinfo is not None:
        today = today.tz_localize(None)
    start = today - pd.Timedelta(days=days)
    at_start = frame[(frame.index <= start) & (frame.index > start - pd.Timedelta(days=lookback_days))]
    firms = set(at_start["Firm"])
    if not firms:
        return None
    frame = frame[frame["Firm"].isin(firms) & (frame.index > start - pd.Timedelta(days=lookback_days))]
    days_in_window = pd.date_range(start, today, freq="D")
    values = []
    for day in days_in_window:
        latest = frame[frame.index <= day].groupby("Firm")["currentPriceTarget"].last()
        values.append(float(latest.mean()))
    series = pd.Series(values, index=days_in_window)
    return float((series / series.cummax() - 1.0).min())


def pt_change(consensus: pd.Series, days: int = 180) -> float | None:
    """Change of the consensus target over the last ``days``."""
    series = consensus.dropna()
    if series.empty:
        return None
    now_day = series.index[-1]
    past = series[series.index <= now_day - pd.Timedelta(days=days)]
    if past.empty or past.iloc[-1] <= 0:
        return None
    return float(series.iloc[-1] / past.iloc[-1] - 1.0)


def pt_max_drawdown(consensus: pd.Series, days: int = 45) -> float | None:
    """Worst fall of the consensus target from its running peak within ``days``."""
    series = consensus.dropna()
    if series.empty:
        return None
    window = series[series.index > series.index[-1] - pd.Timedelta(days=days)]
    if len(window) < 2:
        return None
    return float((window / window.cummax() - 1.0).min())


def channel_position(current: float | None, history: pd.Series,
                     channel=UPSIDE_CHANNEL, min_points: int = MIN_UPSIDE_POINTS) -> float | None:
    """Where ``current`` sits in the horizontal channel of its own history (0 = floor, 1 = ceiling)."""
    series = pd.to_numeric(history, errors="coerce").dropna()
    if current is None or len(series) < min_points:
        return None
    low, high = series.quantile(channel[0]), series.quantile(channel[1])
    if high <= low:
        return None
    return float((current - low) / (high - low))


# -- fetching -------------------------------------------------------------------


def fetch_readings(ticker: str, fx_to_usd, today: pd.Timestamp | None = None) -> Readings:
    """All readings for one ticker from Yahoo; never raises for missing data."""
    import yfinance as yf

    today = (today or pd.Timestamp.today()).normalize()
    t = yf.Ticker(ticker)
    r = Readings(ticker=ticker)
    v = r.values

    info = _safe(lambda: t.info, {}) or {}
    r.name = info.get("shortName") or info.get("longName") or ticker
    r.currency = (info.get("currency") or "").upper()
    fx = fx_to_usd(r.currency) if r.currency else None

    # Must-have: market cap and EPS in USD.
    cap = info.get("marketCap")
    v["market_cap"] = cap * fx if cap and fx else None
    eps = info.get("trailingEps")
    income = _safe(lambda: t.income_stmt, pd.DataFrame())
    eps_currency_fx = fx
    if eps is None and _latest(income, "Basic EPS") is not None:
        # Newest fiscal year; Yahoo's column order is not guaranteed.
        eps = _latest(income, "Basic EPS")
        fin_currency = (info.get("financialCurrency") or r.currency).upper()
        eps_currency_fx = fx_to_usd(fin_currency) if fin_currency else None
        r.notes.append("EPS z ostatniego sprawozdania rocznego (brak TTM)")
    v["eps_ttm"] = eps * eps_currency_fx if eps is not None and eps_currency_fx else None

    earnings = _safe(lambda: t.earnings_estimate, pd.DataFrame())
    revenue = _safe(lambda: t.revenue_estimate, pd.DataFrame())
    v["eps_analysts"] = _cell(earnings, "+1y", "numberOfAnalysts")
    v["revenue_est_2y"] = average_growth(_cell(revenue, "0y", "growth"), _cell(revenue, "+1y", "growth"))
    v["eps_est_2y"] = average_growth(_cell(earnings, "0y", "growth"), _cell(earnings, "+1y", "growth"))
    growth = _safe(lambda: t.growth_estimates, pd.DataFrame())
    v["eps_est_5y"] = _cell(growth, "LTG", "stockTrend")
    v["cfo_est_2y"] = None  # Yahoo publishes no cash-flow forecasts

    # Five-year changes from annual statements.
    cashflow = _safe(lambda: t.cashflow, pd.DataFrame())
    for rule, frame, row in (
        ("revenue_5y", income, "Total Revenue"),
        ("eps_5y", income, "Basic EPS"),
        ("cfo_5y", cashflow, "Operating Cash Flow"),
    ):
        series = _row(frame, row)
        value, span = change_over_years(series) if series is not None else (None, None)
        v[rule] = value
        if value is not None and span is not None and span < YEARS_FOR_CHANGE - 0.5:
            r.notes.append(f"{rule}: przeliczone z {span:.1f} lat")

    v["ebitda_margin"] = info.get("ebitdaMargins")

    balance = _safe(lambda: t.balance_sheet, pd.DataFrame())
    assets = _latest(balance, "Total Assets")
    equity = _latest(balance, "Stockholders Equity")
    liabilities = _latest(balance, "Total Liabilities Net Minority Interest")
    if liabilities is None and assets is not None and equity is not None:
        liabilities = assets - equity
    v["altman"] = altman_z_nonmanufacturing(
        _latest(balance, "Working Capital"), _latest(balance, "Retained Earnings"),
        _latest(income, "EBIT"), equity, assets, liabilities,
    )

    # Price-target rules, from the rebuilt consensus.
    actions = _safe(lambda: t.upgrades_downgrades, pd.DataFrame())
    history = _safe(lambda: t.history(period=f"{UPSIDE_HISTORY_YEARS + 1}y", auto_adjust=False), pd.DataFrame())
    first_ms = info.get("firstTradeDateMilliseconds")
    if first_ms:
        r.years_since_ipo = (today - pd.Timestamp(first_ms, unit="ms")).days / 365.25

    # Yahoo's own consensus; replaced below by the rebuilt one when there is
    # target history, so the upside shown is the upside that was scored.
    r.price_target = info.get("targetMeanPrice")
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if r.price_target and price:
        r.upside_now = r.price_target / price - 1.0

    if actions is None or actions.empty:
        v["pt_change_180d"] = v["pt_drawdown_45d"] = v["upside_vs_history"] = None
        r.notes.append("brak historii cen docelowych u Yahoo")
    else:
        actions = adjust_for_splits(actions, _safe(lambda: t.splits, None))
        daily = consensus_targets(actions, pd.date_range(today - pd.Timedelta(days=200), today, freq="D"))
        v["pt_change_180d"] = pt_change(daily, 180)
        v["pt_drawdown_45d"] = anchored_drawdown(actions, today, 45)
        v["upside_vs_history"] = _upside_channel(actions, history, today, r)

    return r


def _upside_channel(actions, history, today, readings: Readings) -> float | None:
    if history is None or history.empty or "Close" not in history:
        return None
    close = history["Close"].dropna().copy()
    if close.empty:
        return None
    close.index = pd.DatetimeIndex(close.index).tz_localize(None)
    months = pd.date_range(today - pd.DateOffset(years=UPSIDE_HISTORY_YEARS), today, freq="ME")
    targets = consensus_targets(actions, months)
    prices = close.reindex(months, method="ffill")
    upside = (targets / prices - 1.0).dropna()
    now_target = consensus_targets(actions, [today]).iloc[0]
    now_price = float(close.iloc[-1])
    current = (now_target / now_price - 1.0) if now_target == now_target and now_price else None
    if current is not None:
        readings.price_target = float(now_target)
        readings.upside_now = current
    position = channel_position(current, upside)
    if position is None and current is not None:
        readings.notes.append(f"upside: za krótka historia ({len(upside)} mies.)")
    return position


def _safe(fn, default):
    try:
        value = fn()
    except Exception:  # noqa: BLE001 - a missing table is data, not an error
        return default
    return default if value is None else value


def _row(frame: pd.DataFrame, name: str) -> pd.Series | None:
    if frame is None or frame.empty or name not in frame.index:
        return None
    series = frame.loc[name]
    series.index = pd.DatetimeIndex(series.index)
    return series


def _latest(frame: pd.DataFrame, name: str) -> float | None:
    series = _row(frame, name)
    if series is None:
        return None
    series = pd.to_numeric(series, errors="coerce").dropna().sort_index()
    return float(series.iloc[-1]) if not series.empty else None


def _cell(frame: pd.DataFrame, row: str, column: str) -> float | None:
    if frame is None or frame.empty or row not in frame.index or column not in frame.columns:
        return None
    value = pd.to_numeric(pd.Series([frame.loc[row, column]]), errors="coerce").iloc[0]
    return None if pd.isna(value) else float(value)
