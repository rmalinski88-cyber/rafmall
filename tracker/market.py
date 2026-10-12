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
    "pullback_max_age": 15,  # impulse must be within this many bars
    "pullback_pct": 0.03,    # low within 3% above the EMA (or under it) counts as a touch
    "impulse_atr_multiple": 1.5,
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

    # The run of closes above the EMA must end today and be exactly `hold`
    # long, so the setup is reported once, on the day it is confirmed.
    if not above[-hold:].all():
        return None
    run = 0
    for flag in above[::-1]:
        if not flag:
            break
        run += 1
    if run != hold:
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


def ema_pullback_entry(ticker: str, name: str, prices: pd.DataFrame, cfg: dict) -> Setup | None:
    """Rafał's actual entry (the ARB example): impulse through EMA30 on volume,
    a correction back to the rising EMA that does not break it, then the first
    up-close off the EMA.  Fires on that up-close.

    impulse  : within the last `pullback_max_age` bars, a close crosses above
               EMA, volume >= volume_multiple x prior average, bar range >= atr
    correction: after the impulse, the low comes within `pullback_pct` of the EMA
               (or dips under intraday) while closes stay above it; EMA is rising
    entry    : today closes above yesterday and above EMA; today's low touched
               the pullback zone or yesterday's did
    """
    close = prices["close"].astype(float)
    high = prices["high"].astype(float)
    low = prices["low"].astype(float)
    volume = prices["volume"].astype(float)
    n = len(close)
    win, vol_mult = cfg["volume_window"], cfg["volume_multiple"]
    max_age, zone = cfg["pullback_max_age"], cfg["pullback_pct"]
    if n < cfg["ema_len"] + win + max_age + 2:
        return None

    line = ema(close, cfg["ema_len"])
    atr_series = (high - low).rolling(14).mean()
    above = (close > line).to_numpy()

    # today's entry bar
    if not (close.iloc[-1] > close.iloc[-2] and above[-1] and line.iloc[-1] > line.iloc[-3]):
        return None

    # find the most recent impulse bar within max_age
    impulse = None
    for i in range(n - 2, n - 2 - max_age, -1):
        if i < win + 1:
            break
        crossed = above[i] and not above[i - 1]
        avg_vol = float(volume.iloc[i - win:i].mean())
        vol_ok = avg_vol > 0 and float(volume.iloc[i]) >= vol_mult * avg_vol
        range_ok = float(high.iloc[i] - low.iloc[i]) >= float(atr_series.iloc[i]) * cfg["impulse_atr_multiple"]
        if crossed and vol_ok and range_ok:
            impulse = i
            break
    if impulse is None:
        return None

    # correction: between impulse and today, closes stay above EMA, and some
    # low came within `zone` of the EMA (the pullback itself)
    seg = slice(impulse + 1, n - 1)
    if not above[seg].all():
        return None
    gap = (low.iloc[seg] / line.iloc[seg] - 1.0)
    if gap.empty or float(gap.min()) > zone:
        return None  # never came back to the average: no correction, just a run-up
    # Report once: today must be the FIRST up-close since the pullback low.
    low_idx = impulse + 1 + int(np.argmin(gap.to_numpy()))
    for j in range(low_idx + 1, n - 1):
        if close.iloc[j] > close.iloc[j - 1]:
            return None
    corr_vol = float(volume.iloc[seg].mean())
    impulse_vol = float(volume.iloc[impulse])
    if corr_vol >= impulse_vol:
        return None  # correction on higher volume than the impulse is distribution

    last = float(close.iloc[-1])
    ema_last = float(line.iloc[-1])
    impulse_day = pd.Timestamp(close.index[impulse]).date()
    impulse_ratio = impulse_vol / float(volume.iloc[impulse - win:impulse].mean())
    return Setup(
        rule="pullback",
        ticker=ticker, name=name,
        headline=f"wejście po korekcie do EMA{cfg['ema_len']}: impuls {impulse_day} ({impulse_ratio:.1f}× wol.)",
        detail=f"kurs {last:.4g}, EMA {ema_last:.4g} ({last / ema_last - 1:+.1%}); "
               f"najniżej w korekcie {float(gap.min()):+.1%} od EMA; wolumen korekty {corr_vol / impulse_vol:.0%} impulsu",
        strength=impulse_ratio * (1.0 + (n - 1 - impulse) / max_age),
        day=pd.Timestamp(close.index[-1]).date(),
        last_close=last,
        avg_dollar_volume=float((close * volume).tail(20).mean()),
    )


RULES = {
    "pullback": ema_pullback_entry,  # the ARB setup: impulse, correction to EMA30, entry
    "ema30": ema_break_and_hold,     # simpler: break + 3-day hold
}


@dataclass
class MarketScan:
    run_date: str
    setups: list[Setup] = field(default_factory=list)
    checked: int = 0
    skipped_illiquid: int = 0
    warnings: list[str] = field(default_factory=list)
