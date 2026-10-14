"""Trela runner end to end with a fake fetcher (no network)."""

from __future__ import annotations

import pandas as pd

from screener.trela.data import Readings
from screener.trela.run import render_console, run_trela, write_csv, write_html
from screener.trela.scoring import load_model


def _fake(ticker):
    strong = {
        "revenue_5y": 1.2, "revenue_est_2y": 0.25, "eps_5y": 2.0, "eps_est_2y": 0.3, "eps_est_5y": None,
        "cfo_5y": 1.8, "cfo_est_2y": None, "ebitda_margin": 0.45, "altman": 5.0,
        "pt_drawdown_45d": -0.01, "pt_change_180d": 0.15, "upside_vs_history": 0.8,
        "market_cap": 500e9, "eps_analysts": 30, "eps_ttm": 4.0,
    }
    weak = {**strong, "revenue_est_2y": 0.05, "altman": 1.2, "ebitda_margin": 0.1}
    cut = {**strong, "pt_drawdown_45d": -0.12}
    values = {"AAA": strong, "BBB": weak, "CCC": cut}[ticker]
    return Readings(ticker=ticker, values=values, years_since_ipo=10, upside_now=0.2,
                    notes=["test"])


def test_runner_ranks_flags_and_reports(tmp_path):
    model = load_model("config/trela.yml")
    universe = pd.DataFrame({"ticker": ["BBB", "CCC", "AAA"], "name": ["Weak", "Cut", "Strong"]})
    scores, dropped, readings = run_trela(universe, model, _fake)

    assert [s.ticker for s in scores] == ["AAA", "BBB", "CCC"]   # flagged CCC last despite points
    assert {r.id for r in dropped} == {"eps_est_5y", "cfo_est_2y"}
    assert scores[0].max_total == 129 - 5 - 5
    assert readings["AAA"].name == "Strong"

    text = render_console(scores, dropped, readings, model)
    assert "FLAGA" in text and "Strong" in text
    write_csv(scores, readings, model, tmp_path / "t.csv")
    write_html(scores, dropped, readings, model, tmp_path / "t.html")
    assert "Strong" in (tmp_path / "t.html").read_text(encoding="utf-8")
    assert (tmp_path / "t.csv").read_text(encoding="utf-8").count("\n") == 4


def test_fetch_error_is_contained():
    model = load_model("config/trela.yml")
    universe = pd.DataFrame({"ticker": ["AAA", "ERR"], "name": ["A", "E"]})

    def fetch(t):
        if t == "ERR":
            raise RuntimeError("boom")
        return _fake("AAA")

    scores, _, readings = run_trela(universe, model, fetch)
    assert len(scores) == 2
    assert "boom" in readings["ERR"].notes[0]


def test_companies_without_target_history_get_their_own_list(tmp_path):
    from screener.trela.run import split_by_pt_data

    def fetch(t):
        r = _fake("AAA")
        if t == "ASIA":
            r.values = {**r.values, "pt_change_180d": None, "pt_drawdown_45d": None, "upside_vs_history": None}
        r.ticker = t
        return r

    model = load_model("config/trela.yml")
    universe = pd.DataFrame({"ticker": ["AAA", "ASIA"], "name": ["A", "Asia Co"]})
    scores, dropped, readings = run_trela(universe, model, fetch)
    full, partial = split_by_pt_data(scores)
    assert [s.ticker for s in full] == ["AAA"]
    assert [s.ticker for s in partial] == ["ASIA"]
    text = render_console(scores, dropped, readings, model)
    assert "BEZ HISTORII CENY DOCELOWEJ" in text
    write_html(scores, dropped, readings, model, tmp_path / "t.html")
    assert "Bez historii ceny docelowej" in (tmp_path / "t.html").read_text(encoding="utf-8")
