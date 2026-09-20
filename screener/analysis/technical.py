"""Technical indicators and the per-ticker technical metric set.

All indicators are implemented directly rather than pulled from a TA library:
the set is small, and it keeps the dependency list to pandas/numpy so the tool
installs cleanly anywhere.  RSI and ATR use Wilder's original smoothing
(SMA seed, then the 1/n recursive update), not a plain EMA.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = {"1m": 21, "3m": 63, "6m": 126, "12m": 252}


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def wilder_smooth(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing: SMA of the first ``period`` values, then recursion.

    ``ewm(alpha=1/period)`` alone seeds from the first observation, which
    drifts from the textbook values for a hundred-odd bars; seeding with the
    SMA fixes that.
    """
    values = series.to_numpy(dtype=float)
    out = np.full(values.shape, np.nan)
    if len(values) < period:
        return pd.Series(out, index=series.index)

    seed = np.nanmean(values[:period])
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        current = values[i]
        if np.isnan(current):
            out[i] = prev
            continue
        prev = (prev * (period - 1) + current) / period
        out[i] = prev
    return pd.Series(out, index=series.index)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's Relative Strength Index."""
    delta = close.diff()
    # Drop the leading NaN before smoothing.  Keeping it as a zero would both
    # dilute the seed average and shift every value one bar early.
    gain = delta.clip(lower=0.0).iloc[1:]
    loss = (-delta).clip(lower=0.0).iloc[1:]

    avg_gain = wilder_smooth(gain, period).reindex(close.index)
    avg_loss = wilder_smooth(loss, period).reindex(close.index)

    # A flat or purely rising window has zero average loss: RSI is 100 by
    # definition there, and 50 when neither side moved at all.
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    both_flat = (avg_gain == 0.0) & (avg_loss == 0.0)
    out = out.mask(avg_loss == 0.0, 100.0)
    out = out.mask(both_flat, 50.0)
    return out.where(avg_gain.notna())


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns ``(macd_line, signal_line, histogram)``."""
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line, macd_line - signal_line


def true_range(frame: pd.DataFrame) -> pd.Series:
    prev_close = frame["close"].shift(1)
    ranges = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range, Wilder-smoothed."""
    return wilder_smooth(true_range(frame).fillna(0.0), period)


def trailing_return(close: pd.Series, days: int) -> float | None:
    """Simple return over the last ``days`` bars, or ``None`` if too short."""
    if len(close) <= days:
        return None
    start, end = close.iloc[-days - 1], close.iloc[-1]
    if not np.isfinite(start) or start <= 0:
        return None
    return float(end / start - 1.0)


def max_drawdown(close: pd.Series) -> float | None:
    """Worst peak-to-trough decline over the series, as a negative fraction."""
    if close.empty:
        return None
    running_peak = close.cummax()
    drawdown = close / running_peak - 1.0
    value = float(drawdown.min())
    return value if np.isfinite(value) else None


def compute_technical_metrics(
    prices: pd.DataFrame, benchmark: pd.Series | None = None
) -> dict:
    """Every technical figure the scorer and the report need, for one ticker.

    ``benchmark`` is the matching index's close series, used for relative
    strength.  Values that cannot be computed from the available history are
    returned as ``None`` so the scorer can skip them.
    """
    if prices is None or prices.empty or "close" not in prices:
        return {}

    close = prices["close"].astype(float)
    volume = prices["volume"].astype(float) if "volume" in prices else pd.Series(dtype=float)
    last = float(close.iloc[-1])

    out: dict = {"last_close": last, "bars": int(len(close))}

    sma50 = sma(close, 50)
    sma200 = sma(close, 200)
    out["sma50"] = _last_finite(sma50)
    out["sma200"] = _last_finite(sma200)
    out["px_vs_sma50"] = _ratio(last, out["sma50"])
    out["px_vs_sma200"] = _ratio(last, out["sma200"])
    out["sma50_vs_sma200"] = _ratio(out["sma50"], out["sma200"])

    out["rsi14"] = _last_finite(rsi(close, 14))

    _, _, hist = macd(close)
    hist_last = _last_finite(hist)
    # Normalised by price so the figure is comparable across tickers and
    # across currencies with wildly different nominal levels.
    out["macd_hist_pct"] = (hist_last / last) if (hist_last is not None and last) else None

    for label, days in TRADING_DAYS.items():
        out[f"ret_{label}"] = trailing_return(close, days)

    window = close.tail(TRADING_DAYS["12m"])
    high_52w, low_52w = float(window.max()), float(window.min())
    out["high_52w"], out["low_52w"] = high_52w, low_52w
    out["dist_52w_high"] = _ratio(last, high_52w)
    span = high_52w - low_52w
    out["pos_52w_range"] = float((last - low_52w) / span) if span > 0 else None
    out["max_drawdown_12m"] = max_drawdown(window)

    atr_last = _last_finite(atr(prices, 14))
    out["atr_pct"] = (atr_last / last) if (atr_last is not None and last) else None

    if not volume.empty:
        vol20 = float(volume.tail(20).mean())
        vol60 = float(volume.tail(60).mean())
        out["avg_volume_20d"] = vol20 if np.isfinite(vol20) else None
        out["volume_trend"] = _ratio(vol20, vol60 if np.isfinite(vol60) else None)
        out["avg_turnover_local"] = (vol20 * last) if np.isfinite(vol20) else None
    else:
        out["avg_volume_20d"] = out["volume_trend"] = out["avg_turnover_local"] = None

    out.update(_relative_strength(close, benchmark))
    return out


def _relative_strength(close: pd.Series, benchmark: pd.Series | None) -> dict:
    """Stock return minus index return over 3m and 6m, on aligned dates."""
    empty = {"rs_3m": None, "rs_6m": None}
    if benchmark is None or benchmark.empty:
        return empty

    joined = pd.concat([close, benchmark.astype(float)], axis=1, join="inner").dropna()
    if joined.empty:
        return empty

    stock, index = joined.iloc[:, 0], joined.iloc[:, 1]
    out = {}
    for label in ("3m", "6m"):
        days = TRADING_DAYS[label]
        stock_ret, index_ret = trailing_return(stock, days), trailing_return(index, days)
        out[f"rs_{label}"] = (
            float(stock_ret - index_ret) if stock_ret is not None and index_ret is not None else None
        )
    return out


def _last_finite(series: pd.Series) -> float | None:
    cleaned = series.dropna()
    if cleaned.empty:
        return None
    value = float(cleaned.iloc[-1])
    return value if np.isfinite(value) else None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    """``numerator/denominator - 1``, guarding against zero and ``None``."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    value = float(numerator) / float(denominator) - 1.0
    return value if np.isfinite(value) else None
