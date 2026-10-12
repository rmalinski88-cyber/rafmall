"""Plain data types shared by every source, the signal builder and the reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

BUY, SELL = "buy", "sell"

# 13F position change kinds.
NEW, ADD, TRIM, EXIT, HOLD = "new", "add", "trim", "exit", "hold"

CHANGE_LABELS = {
    NEW: "NOWA POZYCJA",
    ADD: "ZWIĘKSZENIE",
    TRIM: "ZMNIEJSZENIE",
    EXIT: "SPRZEDAŻ CAŁOŚCI",
    HOLD: "BEZ ZMIAN",
}

SIDE_LABELS = {BUY: "KUPNO", SELL: "SPRZEDAŻ"}


@dataclass(frozen=True)
class Trade:
    """One disclosed transaction by one person in one instrument.

    ``amount_low``/``amount_high`` carry the dollar value.  Congressional
    disclosures only give a bracket ("$1,001 - $15,000"); insider filings give
    an exact figure, in which case both bounds are equal.
    """

    source: str  # "congress" | "insider"
    actor: str
    role: str
    ticker: str
    side: str  # BUY | SELL
    traded: date | None
    reported: date | None
    amount_low: float | None = None
    amount_high: float | None = None
    shares: float | None = None
    price: float | None = None
    planned: bool = False  # sale under a pre-arranged 10b5-1 plan
    detail: str = ""

    @property
    def amount_mid(self) -> float | None:
        if self.amount_low is None:
            return None
        if self.amount_high is None:
            return self.amount_low
        return (self.amount_low + self.amount_high) / 2.0

    @property
    def lag_days(self) -> int | None:
        """Days between the trade and the public disclosure."""
        if self.traded is None or self.reported is None:
            return None
        return (self.reported - self.traded).days

    @property
    def key(self) -> str:
        """Stable identity, used to tell new trades from ones already seen."""
        parts = [
            self.source, self.actor, self.ticker, self.side,
            str(self.traded or ""), str(self.reported or ""),
            f"{self.shares or ''}", f"{self.amount_low or ''}",
        ]
        return "|".join(parts)


@dataclass(frozen=True)
class Holding:
    """One line of a 13F information table, aggregated by CUSIP."""

    issuer: str
    cusip: str
    value: float  # USD
    shares: float
    put_call: str = ""  # "", "PUT" or "CALL"
    ticker: str | None = None


@dataclass(frozen=True)
class Fund:
    key: str
    name: str
    manager: str
    cik: int


@dataclass
class FundChange:
    issuer: str
    cusip: str
    ticker: str | None
    kind: str
    shares_now: float
    shares_prev: float
    value_now: float
    value_prev: float
    weight_now: float | None  # share of the fund's reported portfolio
    put_call: str = ""

    @property
    def share_change(self) -> float | None:
        if not self.shares_prev:
            return None
        return self.shares_now / self.shares_prev - 1.0


@dataclass
class FundReport:
    fund: Fund
    period_now: date | None
    period_prev: date | None
    filed_now: date | None
    total_value: float
    changes: list[FundChange] = field(default_factory=list)

    def by_kind(self, *kinds: str) -> list[FundChange]:
        return [c for c in self.changes if c.kind in kinds]
