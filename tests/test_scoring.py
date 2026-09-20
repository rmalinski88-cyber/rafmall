"""Scoring tests - ranking direction, gap handling and coverage."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from screener.analysis.scoring import (
    MIN_RANKABLE,
    MetricSpec,
    build_specs,
    percentile_rank,
    score_universe,
)


def _frame(**columns) -> pd.DataFrame:
    frame = pd.DataFrame(columns)
    frame.index = [f"T{i}" for i in range(len(frame))]
    return frame


def test_percentile_rank_orders_ascending_for_higher_is_better():
    ranked = percentile_rank(pd.Series([1.0, 2.0, 3.0, 4.0]), higher_is_better=True)
    assert ranked.iloc[3] == pytest.approx(100.0)
    assert ranked.iloc[0] == pytest.approx(25.0)
    assert ranked.is_monotonic_increasing


def test_percentile_rank_inverts_for_lower_is_better():
    ranked = percentile_rank(pd.Series([1.0, 2.0, 3.0, 4.0]), higher_is_better=False)
    # Smallest value is best, so it takes the top rank.
    assert ranked.iloc[0] == pytest.approx(100.0)
    assert ranked.iloc[3] == pytest.approx(25.0)


def test_percentile_rank_preserves_missing_values():
    ranked = percentile_rank(pd.Series([1.0, np.nan, 3.0, 4.0]), higher_is_better=True)
    assert np.isnan(ranked.iloc[1])
    assert ranked.notna().sum() == 3


def test_metric_with_too_few_reporters_is_dropped_entirely():
    too_few = [1.0] + [np.nan] * 5
    assert len(too_few) - 1 > MIN_RANKABLE  # the series is long; the data is not
    ranked = percentile_rank(pd.Series(too_few), higher_is_better=True)
    assert ranked.isna().all()


def test_infinities_are_treated_as_missing():
    ranked = percentile_rank(pd.Series([1.0, np.inf, 3.0, 4.0]), higher_is_better=True)
    assert np.isnan(ranked.iloc[1])


def test_ties_share_a_rank():
    ranked = percentile_rank(pd.Series([5.0, 5.0, 1.0, 9.0]), higher_is_better=True)
    assert ranked.iloc[0] == pytest.approx(ranked.iloc[1])


def test_build_specs_reads_weight_and_direction():
    specs = build_specs(
        {
            "fundamental": {"revenue_growth": {"weight": 2.0, "direction": "high"}},
            "technical": {"atr_pct": {"weight": 1.0, "direction": "low"}},
        }
    )
    by_key = {s.key: s for s in specs}
    assert by_key["revenue_growth"].higher_is_better is True
    assert by_key["atr_pct"].higher_is_better is False
    assert by_key["revenue_growth"].weight == 2.0


def test_build_specs_accepts_a_bare_number_as_weight():
    specs = build_specs({"fundamental": {"revenue_growth": 3.0}})
    assert specs[0].weight == 3.0
    assert specs[0].higher_is_better is True


def test_build_specs_rejects_an_unknown_direction():
    with pytest.raises(ValueError, match="direction"):
        build_specs({"fundamental": {"revenue_growth": {"weight": 1.0, "direction": "sideways"}}})


def test_build_specs_rejects_an_empty_profile():
    with pytest.raises(ValueError, match="no metrics"):
        build_specs({"fundamental": {}, "technical": {}})


def test_zero_weight_metrics_are_skipped():
    specs = build_specs({"fundamental": {"revenue_growth": 0.0, "gross_margin": 1.0}})
    assert [s.key for s in specs] == ["gross_margin"]


def _simple_specs() -> list[MetricSpec]:
    return [
        MetricSpec("revenue_growth", "fundamental", 1.0, True),
        MetricSpec("debt_to_equity", "fundamental", 1.0, False),
        MetricSpec("ret_12m", "technical", 1.0, True),
    ]


def test_score_universe_produces_group_and_composite_scores():
    frame = _frame(
        ticker=["A", "B", "C", "D"],
        revenue_growth=[0.5, 0.3, 0.1, -0.1],
        debt_to_equity=[0.1, 0.5, 1.0, 2.0],
        ret_12m=[0.8, 0.2, 0.0, -0.3],
    )
    scored = score_universe(frame, _simple_specs(), {"fundamental": 0.5, "technical": 0.5})

    # A leads on every metric, so it must top every score.
    assert scored["fundamental_score"].idxmax() == scored.index[0]
    assert scored["technical_score"].idxmax() == scored.index[0]
    assert scored["composite_score"].idxmax() == scored.index[0]
    assert scored["fundamental_coverage"].eq(1.0).all()


def test_missing_metric_reduces_coverage_but_not_the_score():
    frame = _frame(
        ticker=["A", "B", "C", "D"],
        revenue_growth=[0.5, 0.3, 0.1, -0.1],
        debt_to_equity=[np.nan, 0.5, 1.0, 2.0],
        ret_12m=[0.8, 0.2, 0.0, -0.3],
    )
    scored = score_universe(frame, _simple_specs(), {"fundamental": 0.5, "technical": 0.5})

    # A reports one of two fundamental metrics: half the weight, and its score
    # is that single metric's rank rather than a zero-filled average.
    assert scored.loc["T0", "fundamental_coverage"] == pytest.approx(0.5)
    assert scored.loc["T0", "fundamental_score"] == pytest.approx(100.0)
    assert scored.loc["T1", "fundamental_coverage"] == pytest.approx(1.0)


def test_weights_actually_shift_the_ranking():
    # A and B are mirror images; C and D only exist so the metrics clear
    # MIN_RANKABLE and get ranked at all.
    frame = _frame(
        ticker=["A", "B", "C", "D"],
        revenue_growth=[0.9, 0.1, 0.5, 0.4],
        gross_margin=[0.1, 0.9, 0.5, 0.4],
    )
    weights = {"fundamental": 1.0, "technical": 0.0}

    growth_heavy = score_universe(
        frame,
        [
            MetricSpec("revenue_growth", "fundamental", 10.0, True),
            MetricSpec("gross_margin", "fundamental", 1.0, True),
        ],
        weights,
    )
    margin_heavy = score_universe(
        frame,
        [
            MetricSpec("revenue_growth", "fundamental", 1.0, True),
            MetricSpec("gross_margin", "fundamental", 10.0, True),
        ],
        weights,
    )

    assert growth_heavy.loc["T0", "composite_score"] > growth_heavy.loc["T1", "composite_score"]
    assert margin_heavy.loc["T1", "composite_score"] > margin_heavy.loc["T0", "composite_score"]


def test_composite_renormalises_when_a_group_is_missing():
    frame = _frame(
        ticker=["A", "B", "C", "D"],
        revenue_growth=[0.5, 0.3, 0.1, -0.1],
    )
    specs = [MetricSpec("revenue_growth", "fundamental", 1.0, True)]
    scored = score_universe(frame, specs, {"fundamental": 0.4, "technical": 0.6})

    # With no technical metrics at all, the composite is the fundamental score,
    # not 40% of it.
    assert scored["composite_score"].equals(scored["fundamental_score"])


def test_scoring_does_not_mutate_the_input_frame():
    frame = _frame(
        ticker=["A", "B", "C", "D"],
        revenue_growth=[0.5, 0.3, 0.1, -0.1],
    )
    before = frame.copy()
    score_universe(frame, [MetricSpec("revenue_growth", "fundamental", 1.0, True)], {"fundamental": 1.0})
    pd.testing.assert_frame_equal(frame, before)
