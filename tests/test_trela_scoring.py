"""Trela model scoring, checked against the worked example in the course notes."""

from __future__ import annotations

import pytest

from screener.trela.scoring import Rule, load_model, score_company, score_universe


@pytest.fixture(scope="module")
def model():
    return load_model("config/trela.yml")


def test_model_totals_match_the_course(model):
    # Growth 55 + Fundamentals 30 + Value 41 + Must-Have 3 = 129 (slide, meeting 10).
    assert model.max_points == 129
    assert model.pillar_max("growth") == 55
    assert model.pillar_max("fundamentals") == 30
    assert model.pillar_max("value") == 41
    assert model.pillar_max("must_have") == 3
    assert len(model.rules) == 15


def test_linear_points_from_the_notes(model):
    rules = {r.id: r for r in model.rules}
    # "prognozowany wzrost przychodów 16% -> (16 - 10) / (30 - 10) x 10 = 3 pkt"
    assert rules["revenue_est_2y"].points(0.16) == pytest.approx(3.0)
    # "Altman 3,1 -> (3,1 - 1) / 3 x 30 = 21 pkt"
    assert rules["altman"].points(3.1) == pytest.approx(21.0)
    assert rules["altman"].points(0.5) == 0
    assert rules["altman"].points(9.0) == 30


def test_must_have_boundaries(model):
    rules = {r.id: r for r in model.rules}
    assert rules["market_cap"].points(10.0e9) == 0          # equal to worst -> flag (Scrab)
    assert rules["market_cap"].points(50e9) == 1
    assert rules["eps_analysts"].points(3) == 1             # "poniżej trzech = zero"
    assert rules["eps_analysts"].points(2) == 0
    assert rules["eps_ttm"].points(0.50) == 1
    assert rules["eps_ttm"].points(0.49) == 0
    assert rules["pt_drawdown_45d"].points(-0.05) == 0      # 5% drop or more = flag
    assert rules["pt_drawdown_45d"].points(-0.02) == 1


def test_worked_example_total(model):
    # Notes: Growth 40, Altman 21, Upside 18, PT change 6, all must-haves -> 69,0%.
    readings = {
        "altman": 3.1,                 # 21
        "upside_vs_history": 0.6,      # 18
        "pt_change_180d": 0.16,        # 6
        "pt_drawdown_45d": 0.0,        # 1
        "market_cap": 50e9, "eps_analysts": 20, "eps_ttm": 3.0,  # 3
    }
    score = score_company("X", readings, model)
    # 21 + 18 + 6 + 1 + 3 = 49 without growth; add 40 growth points by hand:
    assert score.total == pytest.approx(49)
    assert (score.total + 40) / 129 == pytest.approx(0.690, abs=0.001)


def test_flag_sends_company_to_the_end(model):
    good = {"altman": 4.0, "market_cap": 20e9, "eps_analysts": 10, "eps_ttm": 2.0, "pt_drawdown_45d": 0.0}
    rich_but_cut = {**good, "altman": 4.0, "upside_vs_history": 1.0, "pt_drawdown_45d": -0.08}
    scores, _ = score_universe({"A": good, "B": rich_but_cut}, model)
    assert [s.ticker for s in scores] == ["A", "B"]
    assert scores[1].flagged and not scores[0].flagged


def test_missing_reading_scores_zero_but_never_flags(model):
    score = score_company("X", {"altman": 2.5}, model)
    assert "market_cap" in score.missing
    assert not score.flagged


def test_rule_with_no_data_anywhere_leaves_the_maximum(model):
    readings = {"A": {"altman": 2.0}, "B": {"altman": 3.0}}
    scores, dropped = score_universe(readings, model)
    assert "altman" not in {r.id for r in dropped}
    assert scores[0].max_total == 30
    assert "cfo_est_2y" in {r.id for r in dropped}


def test_young_listing_is_flagged(model):
    score = score_company("X", {"market_cap": 20e9}, model, years_since_ipo=1.5)
    assert score.flagged


def test_descending_rule_scales_the_other_way():
    rule = Rule(id="debt", filar="fundamentals", nazwa="debt", max=5, worst=0.40, best=0.02)
    assert rule.points(0.40) == 0
    assert rule.points(0.02) == 5
    assert rule.points(0.21) == pytest.approx(2.5)
