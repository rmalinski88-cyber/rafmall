"""Market-wide setup scanner: find names that are *starting* a move, anywhere.

The watch-lists say "tell me what my names do"; this says "show me which of
the thousands of listed names just did X".  The symbol universe comes from
the SEC's full registrant list (free), narrowed by liquidity.  Setups are
plain functions over a price frame, so the next rule is one short block.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from screener.analysis.technical import ema

DEFAULTS = {
    "ema_len": 30,
    "hold_days": 3,          # closes above the EMA needed to confirm
    "volume_multiple": 2.0,  # vs 20-day average before the break
    "volume_window": 20,
    "min_avg_dollar_volume": 2_000_000,  # liquidity floor, USD/day
    "min_price": 2.0,        # skip penny stocks
    "max_hold_days": 6,      # a break older than this is not "starting" any more
}


@dataclass
class Setup:
    rule: str
    ticker: str
    name: str
    headline: str
    detail: str
    strength: float
    day: date | None = None
    last_close: float | None = None
    avg_dollar_volume: float | None = None

    @property
    def key(self) -> str:
        return f"{self.rule}|{self.ticker}|{self.day}"


def liquid_enough(prices: pd.DataFrame, cfg: dict) -> bool:
    if prices is None or len(prices) < 60 or "volume" not in prices:
        return False
    close = prices["close"].astype(float)
    if float(close.iloc[-1]) < cfg["min_price"]:
        return False
    dollar = (close * prices["volume"].astype(float)).tail(20).mean()
    return bool(np.isfinite(dollar) and dollar >= cfg["min_avg_dollar_volume"])


def ema_break_and_hold(ticker: str, name: str, prices: pd.DataFrame, cfg: dict) -> Setup | None:
    """Rafał's rule: close crosses above EMA(ema_len), stays above for hold_days
    sessions, and volume on the break or during the hold is >= volume_multiple x
    its prior average.  Fires on the day the hold is confirmed, once."""
    close = prices["close"].astype(float)
    volume = prices["volume"].astype(float)
    n = len(close)
    hold, vol_mult, win = cfg["hold_days"], cfg["volume_multiple"], cfg["volume_window"]
    if n < cfg["ema_len"] + win + hold + 2:
        return None

    line = ema(close, cfg["ema_len"])
    above = (close > line).to_numpy()

    # The hold must end today and be exactly `hold` long, or longer but not
    # older than max_hold_days: we want the start of a move, not its middle.
    if not above[-hold:].all():
        return None
    run = 0
    for flag in above[::-1]:
        if not flag:
            break
        run += 1
    if run > cfg["max_hold_days"] or run >= n:
        return None
    break_idx = n - run  # first bar of the run = the break bar
    if above[break_idx - 1]:
        return None

    avg_before = float(volume.iloc[break_idx - win:break_idx].mean())
    if not avg_before > 0:
        return None
    window_vol = volume.iloc[break_idx:]
    peak_ratio = float(window_vol.max() / avg_before)
    if peak_ratio < vol_mult:
        return None

    last = float(close.iloc[-1])
    ema_last = float(line.iloc[-1])
    dist = last / ema_last - 1.0
    break_day = pd.Timestamp(close.index[break_idx]).date()
    return Setup(
        rule="ema30",
        ticker=ticker, name=name,
        headline=f"nad EMA{cfg['ema_len']} od {run} sesji, wolumen {peak_ratio:.1f}×",
        detail=f"przebicie {break_day}; kurs {last:.2f}, EMA {ema_last:.2f} ({dist:+.1%}); "
               f"ruch od przebicia {last / float(close.iloc[break_idx - 1]) - 1:+.1%}",
        strength=peak_ratio * (1.0 + max(dist, 0.0) * 5),
        day=pd.Timestamp(close.index[-1]).date(),
        last_close=last,
        avg_dollar_volume=float((close * volume).tail(20).mean()),
    )


RULES = {
    "ema30": ema_break_and_hold,
}


@dataclass
class MarketScan:
    run_date: str
    setups: list[Setup] = field(default_factory=list)
    checked: int = 0
    skipped_illiquid: int = 0
    warnings: list[str] = field(default_factory=list)
