"""Turning trades and 13F changes into one signal per ticker.

The score is a transparent tally, not a model: every distinct person or fund
that bought adds its weight, every one that sold subtracts.  Counting people
rather than dollars keeps one large trade from drowning out a crowd, and the
reasons list says exactly what produced each number.

Weights live in the config.  The defaults encode three well-documented facts:
open-market insider *purchases* are the most informative filings; insider
*sales* are weak evidence (diversification, taxes) and pre-planned 10b5-1
sales are nearly none; congressional disclosures can be 45 days late.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import ADD, BUY, EXIT, NEW, SELL, TRIM, FundReport, Trade
from .sources.sec import is_csuite

DEFAULT_WEIGHTS = {
    "insider_buy_csuite": 3.0,
    "insider_buy": 2.0,
    "insider_sell": -0.5,
    "insider_sell_planned": 0.0,
    "congress_buy": 1.0,
    "congress_sell": -1.0,
    "fund_new": 2.0,
    "fund_add": 1.0,
    "fund_trim": -1.0,
    "fund_exit": -2.0,
}

def label_for(score: float) -> str:
    if score >= 3.0:
        return "SILNY POPYT"
    if score >= 1.0:
        return "POPYT"
    if score > -1.0:
        return "MIESZANE"
    if score > -3.0:
        return "PODAŻ"
    return "SILNA PODAŻ"


@dataclass
class TickerSignal:
    ticker: str
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    buyers: set[str] = field(default_factory=set)
    sellers: set[str] = field(default_factory=set)
    buy_usd: float = 0.0
    sell_usd: float = 0.0
    trades: int = 0
    in_portfolio: bool = False
    on_watchlist: bool = False

    @property
    def label(self) -> str:
        return label_for(self.score)

    @property
    def alert(self) -> bool:
        """A holding the smart money is leaving deserves a look first."""
        return self.in_portfolio and self.score <= -1.0


def build_signals(
    trades: list[Trade],
    fund_reports: list[FundReport],
    portfolio: set[str] = frozenset(),
    watchlist: set[str] = frozenset(),
    weights: dict | None = None,
) -> list[TickerSignal]:
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    signals: dict[str, TickerSignal] = {}

    def slot(ticker: str) -> TickerSignal:
        if ticker not in signals:
            signals[ticker] = TickerSignal(ticker, in_portfolio=ticker in portfolio,
                                           on_watchlist=ticker in watchlist)
        return signals[ticker]

    # One vote per (person, ticker, side), weighted by the strongest variant.
    votes: dict[tuple[str, str, str], tuple[float, str]] = {}
    for t in trades:
        s = slot(t.ticker)
        s.trades += 1
        if t.side == BUY:
            s.buy_usd += t.amount_mid or 0.0
        elif t.side == SELL:
            s.sell_usd += t.amount_mid or 0.0

        weight, why = _trade_weight(t, w)
        key = (t.ticker, f"{t.source}:{t.actor}", t.side)
        if key not in votes or abs(weight) > abs(votes[key][0]):
            votes[key] = (weight, why)

    for (ticker, actor, side), (weight, why) in votes.items():
        s = signals[ticker]
        s.score += weight
        (s.buyers if side == BUY else s.sellers).add(actor.split(":", 1)[1])
        s.reasons.append(why)

    for report in fund_reports:
        for change in report.changes:
            if not change.ticker or change.put_call:
                continue  # unmatched issuers and options carry no clean signal
            key = {NEW: "fund_new", ADD: "fund_add", TRIM: "fund_trim", EXIT: "fund_exit"}.get(change.kind)
            if key is None:
                continue
            s = slot(change.ticker)
            s.score += w[key]
            who = report.fund.manager or report.fund.name
            (s.buyers if change.kind in (NEW, ADD) else s.sellers).add(who)
            s.reasons.append(f"{who} (13F): {_fund_word(change.kind)}")

    ordered = sorted(
        signals.values(),
        key=lambda s: (not s.alert, not s.in_portfolio, -abs(s.score), s.ticker),
    )
    return ordered


def _trade_weight(t: Trade, w: dict) -> tuple[float, str]:
    if t.source == "insider":
        if t.side == BUY:
            key = "insider_buy_csuite" if is_csuite(t.role) else "insider_buy"
            return w[key], f"{t.actor} ({t.role or 'insider'}): zakup na rynku"
        if t.planned:
            return w["insider_sell_planned"], f"{t.actor}: sprzedaż wg planu 10b5-1"
        return w["insider_sell"], f"{t.actor} ({t.role or 'insider'}): sprzedaż"
    if t.side == BUY:
        return w["congress_buy"], f"{t.actor} ({t.role}): kupno"
    return w["congress_sell"], f"{t.actor} ({t.role}): sprzedaż"


def _fund_word(kind: str) -> str:
    return {NEW: "nowa pozycja", ADD: "zwiększenie", TRIM: "zmniejszenie", EXIT: "sprzedaż całości"}[kind]


def group_by_ticker(trades: list[Trade]) -> dict[str, list[Trade]]:
    out: dict[str, list[Trade]] = defaultdict(list)
    for t in trades:
        out[t.ticker].append(t)
    return out
