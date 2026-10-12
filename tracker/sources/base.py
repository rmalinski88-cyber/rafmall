"""Feed interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from ..models import Fund, FundReport, Trade


class FeedError(RuntimeError):
    """A feed cannot serve a request at all (bad setup, not a missing ticker)."""


class TradeFeed(ABC):
    name = "base"

    def __init__(self) -> None:
        #: Non-fatal problems collected during a run, shown in reports.
        self.warnings: list[str] = []

    @abstractmethod
    def congress_trades(self, since: date) -> list[Trade]:
        """STOCK Act trades disclosed on or after ``since``."""

    @abstractmethod
    def insider_trades(self, ticker: str, since: date) -> list[Trade]:
        """Open-market Form 4 purchases and sales filed on or after ``since``."""

    @abstractmethod
    def fund_report(self, fund: Fund) -> FundReport | None:
        """Latest 13F against the one before it; ``None`` when unavailable."""

    @abstractmethod
    def search_names(self, text: str, limit: int = 15) -> list[tuple[str, str]]:
        """``(ticker, name)`` pairs whose ticker or name matches ``text``."""

    def warn(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)
