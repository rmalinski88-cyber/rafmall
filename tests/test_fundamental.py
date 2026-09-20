"""Fundamental normalisation tests."""

from __future__ import annotations

import math

import pytest

from screener.analysis.fundamental import compute_fundamental_metrics


def test_negative_pe_is_discarded():
    # A loss-making company's "P/E" is not a cheap valuation - it is nothing.
    metrics = compute_fundamental_metrics({"trailing_pe": -14.0})
    assert metrics["trailing_pe"] is None
    assert metrics["earnings_yield"] is None


def test_absurd_multiple_is_discarded():
    assert compute_fundamental_metrics({"trailing_pe": 4000.0})["trailing_pe"] is None
    assert compute_fundamental_metrics({"trailing_pe": 42.0})["trailing_pe"] == 42.0


def test_earnings_yield_inverts_pe():
    assert compute_fundamental_metrics({"trailing_pe": 25.0})["earnings_yield"] == pytest.approx(0.04)


def test_negative_margins_pass_through():
    # Negative profitability is real signal and must survive normalisation.
    metrics = compute_fundamental_metrics({"profit_margin": -0.32, "return_on_equity": -0.11})
    assert metrics["profit_margin"] == pytest.approx(-0.32)
    assert metrics["return_on_equity"] == pytest.approx(-0.11)


def test_fcf_margin_is_derived_from_revenue():
    metrics = compute_fundamental_metrics({"total_revenue": 1000.0, "free_cashflow": 150.0})
    assert metrics["fcf_margin"] == pytest.approx(0.15)


def test_fcf_margin_is_none_without_revenue():
    assert compute_fundamental_metrics({"free_cashflow": 150.0})["fcf_margin"] is None


def test_zero_revenue_does_not_divide_by_zero():
    metrics = compute_fundamental_metrics({"total_revenue": 0.0, "free_cashflow": 10.0})
    assert metrics["fcf_margin"] is None


def test_net_cash_and_ratio_to_market_cap():
    metrics = compute_fundamental_metrics(
        {"total_cash": 500.0, "total_debt": 200.0, "market_cap": 1500.0}
    )
    assert metrics["net_cash"] == pytest.approx(300.0)
    assert metrics["net_cash_to_mcap"] == pytest.approx(0.2)


def test_net_debt_is_negative_net_cash():
    metrics = compute_fundamental_metrics(
        {"total_cash": 100.0, "total_debt": 400.0, "market_cap": 1000.0}
    )
    assert metrics["net_cash_to_mcap"] == pytest.approx(-0.3)


def test_non_numeric_and_nan_become_none():
    metrics = compute_fundamental_metrics(
        {"revenue_growth": "n/a", "gross_margin": None, "operating_margin": float("nan")}
    )
    assert metrics["revenue_growth"] is None
    assert metrics["gross_margin"] is None
    assert metrics["operating_margin"] is None


def test_currency_is_upper_cased():
    assert compute_fundamental_metrics({"currency": "jpy"})["currency"] == "JPY"


def test_empty_payload_yields_all_none_without_raising():
    metrics = compute_fundamental_metrics({})
    assert metrics["market_cap"] is None
    assert metrics["is_profitable"] is False
    assert not any(isinstance(v, float) and math.isnan(v) for v in metrics.values())


def test_profitability_flag_follows_margin():
    assert compute_fundamental_metrics({"profit_margin": 0.12})["is_profitable"] is True
    assert compute_fundamental_metrics({"profit_margin": -0.12})["is_profitable"] is False
