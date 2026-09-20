"""End-to-end pipeline and report tests, driven by the fixture provider."""

from __future__ import annotations

import pandas as pd
import pytest

from screener.config import benchmark_for, load_config, resolve_profile
from screener.pipeline import run_screen
from screener.providers.fixture import FixtureProvider
from screener.report.charts import quadrant_scatter, score_bar, sparkline
from screener.report.console import render_console
from screener.report.html import render_html
from screener.universe import load_universe

CONFIG_PATH = "config/default.yml"
UNIVERSE_PATH = "data/universe_humanoid_asia.csv"


@pytest.fixture(scope="module")
def config() -> dict:
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def universe() -> pd.DataFrame:
    return load_universe(UNIVERSE_PATH)


@pytest.fixture(scope="module")
def result(universe, config):
    return run_screen(universe, FixtureProvider(), config, profile_name="growth")


# -- universe --------------------------------------------------------------


def test_universe_loads_with_expected_columns(universe):
    assert len(universe) >= 30
    for column in ("ticker", "name", "market", "segment", "confidence", "notes"):
        assert column in universe.columns


def test_universe_has_no_duplicate_tickers(universe):
    assert universe["ticker"].duplicated().sum() == 0


def test_every_universe_ticker_maps_to_a_benchmark(universe, config):
    for ticker in universe["ticker"]:
        assert benchmark_for(ticker, config), f"no benchmark for {ticker}"


# -- config ----------------------------------------------------------------


def test_all_declared_profiles_build(config):
    from screener.analysis.scoring import build_specs

    for name in config["profiles"]:
        _, profile = resolve_profile(config, name)
        assert build_specs(profile)


def test_unknown_profile_raises(config):
    with pytest.raises(KeyError, match="unknown scoring profile"):
        resolve_profile(config, "nonexistent")


def test_longest_benchmark_suffix_wins(config):
    # ".TWO" must not be swallowed by the ".TW" rule.
    assert benchmark_for("1234.TWO", config) == config["benchmarks"][".TWO"]
    assert benchmark_for("2330.TW", config) == config["benchmarks"][".TW"]


# -- pipeline --------------------------------------------------------------


def test_screen_returns_a_ranking(result):
    assert not result.ranked.empty
    assert result.screened_count == len(result.ranked) + len(result.rejected)


def test_ranking_is_sorted_by_composite_score(result):
    scores = result.ranked["composite_score"].dropna()
    assert scores.is_monotonic_decreasing


def test_scores_stay_inside_zero_to_hundred(result):
    for column in ("composite_score", "fundamental_score", "technical_score"):
        values = result.ranked[column].dropna()
        assert values.between(0, 100).all(), f"{column} out of range"


def test_every_rejected_row_carries_a_reason(result):
    if not result.rejected.empty:
        assert result.rejected["excluded_reason"].notna().all()


def test_rejected_and_ranked_do_not_overlap(result):
    assert set(result.ranked["ticker"]) & set(result.rejected["ticker"]) == set()


def test_fixture_provider_is_deterministic(universe, config):
    first = run_screen(universe, FixtureProvider(), config, profile_name="growth")
    second = run_screen(universe, FixtureProvider(), config, profile_name="growth")
    assert list(first.ranked["ticker"]) == list(second.ranked["ticker"])


def test_changing_profile_changes_the_ranking(universe, config):
    growth = run_screen(universe, FixtureProvider(), config, profile_name="growth")
    value = run_screen(universe, FixtureProvider(), config, profile_name="value")
    assert list(growth.ranked["ticker"]) != list(value.ranked["ticker"])


def test_coverage_filter_removes_thin_data_names(universe, config):
    strict = dict(config)
    strict["filters"] = {**config["filters"], "min_fundamental_coverage": 0.99}
    result = run_screen(universe.head(12), FixtureProvider(), strict, profile_name="growth")

    surviving = result.ranked["fundamental_coverage"].dropna()
    assert (surviving >= 0.99).all()


def test_a_disabled_filter_lets_everything_through(universe, config):
    loose = dict(config)
    loose["filters"] = {
        "min_market_cap_usd": None,
        "min_avg_turnover_usd": None,
        "min_price_bars": None,
        "max_debt_to_equity": None,
        "min_fundamental_coverage": None,
    }
    result = run_screen(universe.head(10), FixtureProvider(), loose, profile_name="growth")
    assert len(result.ranked) == 10


def test_market_cap_filter_excludes_small_companies(universe, config):
    strict = dict(config)
    strict["filters"] = {**config["filters"], "min_market_cap_usd": 1e15}
    result = run_screen(universe.head(10), FixtureProvider(), strict, profile_name="growth")

    assert result.ranked.empty
    assert result.rejected["excluded_reason"].str.contains("kapitalizacja").any()


def test_usd_conversion_is_applied(result):
    row = result.ranked.iloc[0]
    if row.get("currency") == "JPY":
        # Market cap in USD must be far smaller than the same figure in yen.
        assert row["market_cap_usd"] < row["market_cap"]


# -- reports ---------------------------------------------------------------


def test_console_report_renders(result):
    text = render_console(result, top=10)
    assert "Screener robotyki humanoidalnej" in text
    assert "nie jest rekomendacja" in text
    assert result.ranked.iloc[0]["ticker"] in text


def test_console_report_survives_an_empty_ranking(universe, config):
    strict = dict(config)
    strict["filters"] = {**config["filters"], "min_market_cap_usd": 1e15}
    empty = run_screen(universe.head(5), FixtureProvider(), strict, profile_name="growth")
    assert "żadna spółka nie przeszła filtrów" in render_console(empty)


def test_html_report_is_written_and_well_formed(result, tmp_path):
    path = render_html(result, tmp_path / "report.html")
    html = path.read_text(encoding="utf-8")

    assert html.startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")
    assert "<svg" in html
    assert result.ranked.iloc[0]["ticker"] in html
    # Dark mode must be declared under both scopes, not just the media query.
    assert 'prefers-color-scheme: dark' in html
    assert ':root[data-theme="dark"]' in html


def test_html_escapes_company_names(universe, config, tmp_path):
    injected = universe.head(6).copy()
    injected.loc[injected.index[0], "name"] = '<script>alert("x")</script>'
    result = run_screen(injected, FixtureProvider(), config, profile_name="growth")

    html = render_html(result, tmp_path / "escaped.html").read_text(encoding="utf-8")
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_sparkline_handles_missing_and_flat_series():
    assert "brak danych" in sparkline(pd.Series(dtype=float))
    flat = pd.Series([10.0] * 30, index=pd.bdate_range("2024-01-01", periods=30))
    assert "<polyline" in sparkline(flat)


def test_score_bar_clamps_out_of_range_values():
    assert "brak wyniku" in score_bar(None)
    assert "<rect" in score_bar(150)
    assert "<rect" in score_bar(-20)


def test_scatter_reports_emptiness_rather_than_drawing_nothing():
    empty = pd.DataFrame(columns=["ticker", "fundamental_score", "technical_score", "composite_score"])
    assert "Brak spółek" in quadrant_scatter(empty)
