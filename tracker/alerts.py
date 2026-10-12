"""Anomaly detection on the watched universe: what moved today, and why it matters.

Each rule is a plain function from a price frame to zero or one alert, so
adding a rule is adding a function.  Thresholds scale with the instrument's
own volatility (ATR) where that makes sense, so a 4% day on a quiet bearing
maker and a 4% day on a pre-revenue battery start-up are not treated alike.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from screener.analysis.technical import atr, sma

OKAZJA, WOLUMEN, RUCH, WYBICIE, TREND, SMART, POZIOM = "okazja", "wolumen", "ruch", "wybicie", "trend", "smart money", "poziom"
KONFLUENCJA = "konfluencja"

DEFAULTS = {
    "volume_multiple": 3.0,  # today's volume vs 20-day average
    "move_atr_multiple": 2.5,  # |daily change| vs ATR(14)
    "dip_default_pct": 20.0,  # buy-the-dip threshold when the CSV gives none
    "pivot_window": 5,  # a bar is a swing high/low if it tops/bottoms this many bars each side
    "pivot_lookback": 90,  # how far back swing levels stay "live"
    "confluence_min": 2,  # alerts on one ticker in one day to call it confluence
}


@dataclass
class Alert:
    kind: str
    ticker: str
    name: str
    headline: str
    detail: str
    score: float  # for ordering: bigger = more unusual
    in_portfolio: bool = False
    on_dip_list: bool = False
    day: date | None = None

    @property
    def key(self) -> str:
        return f"{self.kind}|{self.ticker}|{self.day}"


def detect(ticker: str, name: str, prices: pd.DataFrame, cfg: dict,
           dip_threshold: float | None = None, in_portfolio: bool = False) -> list[Alert]:
    """All alerts for one instrument on its latest bar."""
    if prices is None or len(prices) < 30:
        return []
    close = prices["close"].astype(float)
    volume = prices["volume"].astype(float) if "volume" in prices else None
    last, prev = float(close.iloc[-1]), float(close.iloc[-2])
    day = pd.Timestamp(close.index[-1]).date()
    change = last / prev - 1.0 if prev else 0.0
    common = dict(ticker=ticker, name=name, in_portfolio=in_portfolio,
                  on_dip_list=dip_threshold is not None, day=day)
    out: list[Alert] = []

    # -- volume spike
    if volume is not None and len(volume) >= 21:
        avg20 = float(volume.iloc[-21:-1].mean())
        today = float(volume.iloc[-1])
        if avg20 > 0 and today / avg20 >= cfg["volume_multiple"]:
            mult = today / avg20
            out.append(Alert(WOLUMEN, headline=f"wolumen {mult:.1f}× średniej",
                             detail=f"{today:,.0f} wobec śr. 20 sesji {avg20:,.0f}; kurs {change:+.1%}".replace(",", " "),
                             score=mult, **common))

    # -- price move vs own volatility
    atr_val = atr(prices, 14).dropna()
    if not atr_val.empty and prev:
        atr_pct = float(atr_val.iloc[-1]) / prev
        if atr_pct > 0 and abs(change) >= cfg["move_atr_multiple"] * atr_pct:
            mult = abs(change) / atr_pct
            out.append(Alert(RUCH, headline=f"ruch {change:+.1%} ({mult:.1f}× ATR)",
                             detail=f"typowy dzienny zakres to {atr_pct:.1%}",
                             score=mult, **common))

    # -- 52-week breakout
    window = close.tail(252)
    if len(window) >= 120:
        prior_high, prior_low = float(window.iloc[:-1].max()), float(window.iloc[:-1].min())
        if last > prior_high:
            out.append(Alert(WYBICIE, headline="nowy szczyt 52 tygodni",
                             detail=f"{last:.2f} > {prior_high:.2f}", score=2.0, **common))
        elif last < prior_low:
            out.append(Alert(WYBICIE, headline="nowy dołek 52 tygodni",
                             detail=f"{last:.2f} < {prior_low:.2f}", score=2.0, **common))

    # -- moving-average crosses
    # SMA50 crosses were half of all real alerts and rarely meant anything; SMA200 stays.
    for span in (200,):
        line = sma(close, span)
        if len(line.dropna()) >= 2:
            a, b = float(line.iloc[-2]), float(line.iloc[-1])
            if np.isfinite(a) and np.isfinite(b):
                if prev <= a and last > b:
                    out.append(Alert(TREND, headline=f"przebicie SMA{span} w górę",
                                     detail=f"kurs {last:.2f}, średnia {b:.2f}", score=1.0 + span / 200, **common))
                elif prev >= a and last < b:
                    out.append(Alert(TREND, headline=f"przebicie SMA{span} w dół",
                                     detail=f"kurs {last:.2f}, średnia {b:.2f}", score=1.0 + span / 200, **common))

    # -- swing-level breaks (the "map of highs and lows" idea): every local
    # high/low from the look-back is a level until price closes through it.
    for level, side in swing_levels(prices, cfg["pivot_window"], cfg["pivot_lookback"]):
        if side == "high" and prev <= level < last:
            out.append(Alert(POZIOM, headline=f"przebicie oporu {level:.2f} w górę",
                             detail=f"lokalny szczyt z ostatnich {cfg['pivot_lookback']} sesji; kurs {last:.2f}",
                             score=1.8, **common))
            break
        if side == "low" and prev >= level > last:
            out.append(Alert(POZIOM, headline=f"przebicie wsparcia {level:.2f} w dół",
                             detail=f"lokalny dołek z ostatnich {cfg['pivot_lookback']} sesji; kurs {last:.2f}",
                             score=1.8, **common))
            break

    # -- buy-the-dip
    if dip_threshold is not None and len(window) >= 60:
        high = float(window.max())
        drawdown = 1.0 - last / high if high else 0.0
        sma200 = sma(close, 200).dropna()
        below200 = (not sma200.empty) and last < float(sma200.iloc[-1])
        if drawdown >= dip_threshold / 100.0 or below200:
            why = []
            if drawdown >= dip_threshold / 100.0:
                why.append(f"{drawdown:.0%} poniżej szczytu 52T (próg {dip_threshold:.0f}%)")
            if below200:
                why.append("poniżej SMA200")
            out.append(Alert(OKAZJA, headline="okazja zakupowa wg Twoich progów",
                             detail="; ".join(why), score=3.0 + drawdown * 10, **common))
    return out


def swing_levels(prices: pd.DataFrame, window: int, lookback: int) -> list[tuple[float, str]]:
    """Unbroken swing highs/lows in the look-back, nearest to the last close first.

    A swing high is a bar whose high beats ``window`` bars on each side; it
    stays a level until a later close exceeds it (then it is "spent").  The
    last ``window`` bars cannot be confirmed yet and are skipped.
    """
    high = prices["high"].astype(float).to_numpy()
    low = prices["low"].astype(float).to_numpy()
    close = prices["close"].astype(float).to_numpy()
    n = len(close)
    start = max(window, n - lookback)
    levels: list[tuple[float, str]] = []
    for i in range(start, n - window - 1):
        if high[i] == high[i - window:i + window + 1].max() and close[i + 1:-1].max(initial=-np.inf) <= high[i]:
            levels.append((float(high[i]), "high"))
        if low[i] == low[i - window:i + window + 1].min() and close[i + 1:-1].min(initial=np.inf) >= low[i]:
            levels.append((float(low[i]), "low"))
    last = close[-1]
    return sorted(levels, key=lambda lv: abs(lv[0] - last))


def mark_confluence(alerts: list[Alert], minimum: int = 2) -> list[Alert]:
    """Several independent signals on one ticker in one day beat any single one."""
    by: dict[tuple[str, date | None], list[Alert]] = {}
    for a in alerts:
        if a.kind != SMART:
            by.setdefault((a.ticker, a.day), []).append(a)
    extra = []
    for (ticker, day), group in by.items():
        kinds = {a.kind for a in group}
        if len(kinds) >= minimum:
            first = group[0]
            extra.append(Alert(KONFLUENCJA, ticker=ticker, name=first.name,
                               headline=f"KONFLUENCJA: {', '.join(sorted(kinds))}",
                               detail=" | ".join(a.headline for a in group),
                               score=10.0 + sum(a.score for a in group),
                               in_portfolio=first.in_portfolio, on_dip_list=first.on_dip_list, day=day))
    return alerts + extra


def smart_money_alerts(trades, portfolio: set[str]) -> list[Alert]:
    """One alert per (ticker, side) for brand-new filings."""
    from .models import SIDE_LABELS

    grouped: dict[tuple[str, str], list] = {}
    for t in trades:
        grouped.setdefault((t.ticker, t.side), []).append(t)
    out = []
    for (ticker, side), items in grouped.items():
        who = sorted({t.actor for t in items})
        out.append(Alert(SMART, ticker=ticker, name=ticker,
                         headline=f"{SIDE_LABELS.get(side, side).lower()}: {len(who)} os.",
                         detail=", ".join(who[:4]) + (" …" if len(who) > 4 else ""),
                         score=1.5 + 0.5 * len(who), in_portfolio=ticker in portfolio,
                         day=max((t.reported for t in items if t.reported), default=None)))
    return out


def order(alerts: list[Alert]) -> list[Alert]:
    return sorted(alerts, key=lambda a: (not a.in_portfolio, not a.on_dip_list, a.kind != KONFLUENCJA,
                                         a.kind != OKAZJA, -a.score, a.ticker))


@dataclass
class AlertRun:
    run_date: str
    alerts: list[Alert] = field(default_factory=list)
    checked: int = 0
    warnings: list[str] = field(default_factory=list)
