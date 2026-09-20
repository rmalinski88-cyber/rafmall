"""Indicator tests.

RSI and ATR are checked against naive loop implementations written here from
the textbook definition.  A vectorised indicator that agrees with an
independent straightforward loop on random data is the strongest cheap
evidence that the vectorisation is right.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from screener.analysis.technical import (
    atr,
    compute_technical_metrics,
    macd,
    max_drawdown,
    rsi,
    sma,
    trailing_return,
    true_range,
)


def _series(values) -> pd.Series:
    index = pd.bdate_range("2024-01-01", periods=len(values))
    return pd.Series(values, index=index, dtype=float)


def _frame(n: int = 300, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.018, n)))
    spread = np.abs(rng.normal(0, 0.012, n))
    index = pd.bdate_range("2024-01-01", periods=n)
    return pd.DataFrame(
        {
            "open": np.concatenate([[close[0]], close[:-1]]),
            "high": close * (1 + spread),
            "low": close * (1 - spread),
            "close": close,
            "volume": rng.lognormal(13, 0.3, n).round(),
        },
        index=index,
    )


# -- reference implementations --------------------------------------------


def reference_rsi(values, period: int = 14):
    """Wilder RSI, written the slow obvious way."""
    gains, losses = [], []
    for previous, current in zip(values[:-1], values[1:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    out = [None] * period + [_rsi_from(avg_gain, avg_loss)]

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out.append(_rsi_from(avg_gain, avg_loss))
    return out


def _rsi_from(avg_gain: float, avg_loss: float) -> float:
    if avg_gain == 0.0 and avg_loss == 0.0:
        return 50.0
    if avg_loss == 0.0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


def reference_atr(frame: pd.DataFrame, period: int = 14):
    ranges = []
    closes = frame["close"].tolist()
    highs, lows = frame["high"].tolist(), frame["low"].tolist()
    for i in range(len(frame)):
        if i == 0:
            ranges.append(highs[i] - lows[i])
        else:
            ranges.append(
                max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i - 1]),
                    abs(lows[i] - closes[i - 1]),
                )
            )

    out = [None] * (period - 1)
    current = sum(ranges[:period]) / period
    out.append(current)
    for i in range(period, len(ranges)):
        current = (current * (period - 1) + ranges[i]) / period
        out.append(current)
    return out


# -- tests -----------------------------------------------------------------


def test_sma_matches_manual_mean():
    series = _series(range(1, 11))
    assert sma(series, 3).iloc[-1] == pytest.approx((8 + 9 + 10) / 3)
    # The first window-1 values have no full window and must stay NaN.
    assert sma(series, 3).iloc[:2].isna().all()


def test_rsi_matches_reference_implementation():
    frame = _frame(200, seed=11)
    close = frame["close"]

    got = rsi(close, 14)
    expected = reference_rsi(close.tolist(), 14)

    for position in range(14, len(close)):
        assert got.iloc[position] == pytest.approx(expected[position], rel=1e-9)
    assert got.iloc[:14].isna().all()


def test_rsi_is_100_when_price_only_rises():
    rising = _series([100 + i for i in range(40)])
    assert rsi(rising, 14).iloc[-1] == pytest.approx(100.0)


def test_rsi_is_0_when_price_only_falls():
    falling = _series([200 - i for i in range(40)])
    assert rsi(falling, 14).iloc[-1] == pytest.approx(0.0)


def test_rsi_is_50_on_a_flat_series():
    flat = _series([50.0] * 40)
    assert rsi(flat, 14).iloc[-1] == pytest.approx(50.0)


def test_atr_matches_reference_implementation():
    frame = _frame(120, seed=3)
    got = atr(frame, 14)
    expected = reference_atr(frame, 14)

    for position in range(13, len(frame)):
        assert got.iloc[position] == pytest.approx(expected[position], rel=1e-9)


def test_true_range_uses_previous_close_gap():
    frame = pd.DataFrame(
        {"high": [10.0, 12.0], "low": [9.0, 11.5], "close": [9.5, 12.0]},
        index=pd.bdate_range("2024-01-01", periods=2),
    )
    # Second bar gaps up: |high - prev_close| = 2.5 beats the 0.5 intraday range.
    assert true_range(frame).iloc[1] == pytest.approx(2.5)


def test_macd_histogram_is_line_minus_signal():
    close = _frame(120, seed=5)["close"]
    line, signal, hist = macd(close)
    assert hist.iloc[-1] == pytest.approx(line.iloc[-1] - signal.iloc[-1])


def test_trailing_return_and_none_when_too_short():
    series = _series([100.0, 110.0, 121.0])
    assert trailing_return(series, 2) == pytest.approx(0.21)
    assert trailing_return(series, 10) is None


def test_max_drawdown_finds_worst_peak_to_trough():
    series = _series([100.0, 120.0, 60.0, 90.0])
    assert max_drawdown(series) == pytest.approx(-0.5)


def test_metrics_are_empty_for_empty_prices():
    assert compute_technical_metrics(pd.DataFrame()) == {}


def test_metrics_cover_the_expected_keys():
    frame = _frame(300, seed=2)
    metrics = compute_technical_metrics(frame, benchmark=frame["close"] * 0.99)

    for key in ("last_close", "sma50", "sma200", "rsi14", "ret_12m", "rs_6m", "atr_pct"):
        assert key in metrics

    assert metrics["bars"] == 300
    assert 0.0 <= metrics["rsi14"] <= 100.0
    assert 0.0 <= metrics["pos_52w_range"] <= 1.0
    # Against a benchmark that is a constant multiple of itself, relative
    # strength must be flat.
    assert metrics["rs_6m"] == pytest.approx(0.0, abs=1e-9)


def test_short_history_leaves_long_averages_undefined():
    frame = _frame(60, seed=4)
    metrics = compute_technical_metrics(frame)
    assert metrics["sma200"] is None
    assert metrics["px_vs_sma200"] is None
    assert metrics["sma50"] is not None
