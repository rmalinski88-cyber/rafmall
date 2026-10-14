"""Pure computations behind the Trela readings."""

from __future__ import annotations

import pandas as pd
import pytest

from screener.trela.data import (
    altman_z_nonmanufacturing,
    average_growth,
    change_over_years,
    channel_position,
    consensus_targets,
    pt_change,
    pt_max_drawdown,
)


def _annual(values, start_year=2021):
    index = pd.to_datetime([f"{start_year + i}-12-31" for i in range(len(values))])
    return pd.Series(values, index=index)


def test_change_over_five_full_years_is_the_plain_change():
    change, span = change_over_years(_annual([100, 120, 140, 170, 190, 200], 2020))
    assert change == pytest.approx(1.0, rel=1e-3)
    assert span == pytest.approx(5.0, abs=0.01)


def test_shorter_span_is_projected_to_five_years():
    # 3 years of 10% a year -> 5 years of 10% a year = +61%.
    change, span = change_over_years(_annual([100, 110, 121, 133.1]))
    assert span == pytest.approx(3.0, abs=0.01)
    assert change == pytest.approx(1.1 ** 5 - 1, rel=1e-3)


def test_change_from_a_loss_has_no_rate():
    assert change_over_years(_annual([-5, 2, 4, 6]))[0] is None


def test_nan_columns_are_ignored():
    # Yahoo returns a trailing all-NaN fifth year.
    series = _annual([100, 110, 121, float("nan")])
    change, span = change_over_years(series)
    assert span == pytest.approx(2.0, abs=0.01)


def test_average_growth_is_geometric():
    assert average_growth(0.21, 0.0) == pytest.approx(1.21 ** 0.5 - 1)
    assert average_growth(None, 0.1) is None
    assert average_growth(-1.5, 0.1) is None


def test_altman_matches_the_formula():
    z = altman_z_nonmanufacturing(20, 30, 10, 60, 100, 40)
    assert z == pytest.approx(6.56 * 0.2 + 3.26 * 0.3 + 6.72 * 0.1 + 1.05 * 1.5)
    assert altman_z_nonmanufacturing(None, 30, 10, 60, 100, 40) is None


def _actions(rows):
    frame = pd.DataFrame(rows, columns=["date", "Firm", "currentPriceTarget"])
    return frame.set_index(pd.to_datetime(frame.pop("date")))


def test_consensus_takes_each_firms_latest_target():
    actions = _actions([
        ("2026-01-10", "A", 100), ("2026-03-01", "A", 120),
        ("2026-02-01", "B", 80), ("2026-02-15", "C", 0),   # zero = target withdrawn, ignored
    ])
    series = consensus_targets(actions, pd.to_datetime(["2026-01-20", "2026-03-10"]))
    assert series.iloc[0] == pytest.approx(100)          # only A so far
    assert series.iloc[1] == pytest.approx((120 + 80) / 2)


def test_old_targets_fall_out_of_the_consensus():
    actions = _actions([("2024-01-01", "A", 50), ("2026-01-01", "B", 100)])
    series = consensus_targets(actions, pd.to_datetime(["2026-02-01"]))
    assert series.iloc[0] == pytest.approx(100)


def test_pt_change_and_drawdown():
    days = pd.date_range("2026-01-01", periods=200, freq="D")
    values = [100.0] * 20 + [130.0] * 160 + [120.0] * 20
    series = pd.Series(values, index=days)
    assert pt_change(series, 180) == pytest.approx(0.20)
    assert pt_max_drawdown(series, 45) == pytest.approx(120 / 130 - 1)


def test_channel_position():
    history = pd.Series([0.10] * 10 + [0.20] * 10 + [0.30] * 10)
    assert channel_position(0.30, history, min_points=24) == pytest.approx(1.0)
    assert channel_position(0.10, history, min_points=24) == pytest.approx(0.0)
    assert channel_position(0.20, pd.Series([0.1, 0.2]), min_points=24) is None
