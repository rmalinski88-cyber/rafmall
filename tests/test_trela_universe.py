"""Trela's US universe, screener prefilter and report extras (no network)."""

from __future__ import annotations

import pandas as pd

from screener.trela.run import discord_summary, prefilter_reason, render_console, run_trela, write_csv, write_html
from screener.trela.scoring import load_model
from screener.trela.universe import build_query, humanoid_tickers, parse_rows, us_universe
from tests.test_trela_run import _fake


def _payload(rows):
    return {"data": [{"s": s, "d": d} for s, d in rows]}


def test_rows_keep_us_exchanges_and_one_line_per_company():
    payload = _payload([
        ("NASDAQ:GOOGL", ["GOOGL", "Alphabet Inc.", 2.0e12, "NASDAQ", 5e9]),
        ("NASDAQ:GOOG", ["GOOG", "Alphabet Inc.", 2.0e12, "NASDAQ", 3e9]),
        ("NYSE:BRK.B", ["BRK.B", "Berkshire Hathaway Inc.", 1.0e12, "NYSE", 1e9]),
        ("OTC:FANUY", ["FANUY", "Fanuc ADR", 3.0e10, "OTC", 1e7]),
        ("NYSE:SMALL", ["SMALL", "Small Co", 5.0e9, "NYSE", 1e7]),
        ("NYSE:PFD/PA", ["PFD/PA", "Preferred", 2.0e10, "NYSE", 1e7]),
    ])
    frame = parse_rows(payload, 10e9)
    assert list(frame["ticker"]) == ["GOOGL", "BRK-B"]


def test_query_asks_for_us_stocks_and_adrs_above_the_cap():
    query = build_query(10e9)
    lefts = {f["left"]: f["right"] for f in query["filter"]}
    assert lefts["market_cap_basic"] == 10e9
    assert set(lefts["type"]) == {"stock", "dr"}


def test_humanoid_list_maps_asian_names_to_adrs():
    tickers = humanoid_tickers()
    assert {"TSM", "SONY", "TM", "NVDA", "TER"} <= tickers
    assert not any("." in t for t in tickers)


def test_unreachable_tradingview_falls_back_and_says_so():
    def broken(_cap):
        raise ConnectionError("blocked")

    frame, source = us_universe(fetch=broken, humanoids={"TER", "NVDA"})
    assert set(frame["ticker"]) == {"TER", "NVDA"}
    assert "ZAPASOWO" in source and frame["humanoid"].all()


def test_small_humanoid_name_is_added_to_the_scan():
    def fetch(_cap):
        return pd.DataFrame({"ticker": ["NVDA", "AAPL"], "name": ["NVIDIA", "Apple"]})

    frame, _ = us_universe(fetch=fetch, humanoids={"NVDA", "OUST"})
    assert set(frame["ticker"]) == {"NVDA", "AAPL", "OUST"}
    assert dict(zip(frame["ticker"], frame["humanoid"])) == {"NVDA": True, "AAPL": False, "OUST": True}


def test_prefilter_cuts_on_readings_but_not_on_missing_data():
    model = load_model("config/trela.yml")
    assert prefilter_reason({"eps_ttm": 2.0, "altman": 3.0}, model.prefilter) == ""
    assert "Altman" in prefilter_reason({"altman": 1.5}, model.prefilter)
    assert prefilter_reason({}, model.prefilter) == ""


def test_run_with_prefilter_keeps_humanoids_and_reports_cuts(tmp_path):
    model = load_model("config/trela.yml")

    def fetch(t):
        r = _fake({"WEAK": "BBB", "ROBO": "BBB"}.get(t, "AAA"))
        r.ticker = t
        if t == "ABOVE":
            r.upside_now = -0.05
        return r

    universe = pd.DataFrame({"ticker": ["AAA", "WEAK", "ROBO", "ABOVE"], "name": ["A", "Weak", "Robot", "Above"],
                             "humanoid": [False, False, True, False]})
    scores, dropped, readings = run_trela(universe, model, fetch, workers=3, prefilter=True)
    ranked = {s.ticker for s in scores}
    assert "WEAK" not in ranked and readings["WEAK"].prefiltr      # Altman 1.2 < 2
    assert "ROBO" in ranked                                         # same numbers, but humanoid

    text = render_console(scores, dropped, readings, model, source="test")
    assert "odrzucił 1" in text and "Spółki humanoidalne w rankingu: ROBO" in text
    assert "nie kupuj teraz" in text
    write_html(scores, dropped, readings, model, tmp_path / "t.html", source="test")
    html = (tmp_path / "t.html").read_text(encoding="utf-8")
    assert "Twoje spółki humanoidalne" in html and "Odrzucone przez filtr wstępny (1)" in html
    write_csv(scores, readings, model, tmp_path / "t.csv")
    assert "filtr wstępny" in (tmp_path / "t.csv").read_text(encoding="utf-8")
    message = discord_summary(scores, readings, model, "test")
    assert "Humanoidy: ROBO" in message and len(message) < 2000


def test_data_guard_warns_when_target_history_is_missing():
    model = load_model("config/trela.yml")

    def fetch(t):
        r = _fake("AAA")
        r.ticker = t
        r.values = {**r.values, "pt_change_180d": None, "pt_drawdown_45d": None, "upside_vs_history": None}
        return r

    universe = pd.DataFrame({"ticker": ["X", "Y"], "name": ["X", "Y"]})
    scores, dropped, readings = run_trela(universe, model, fetch)
    assert "UWAGA" in render_console(scores, dropped, readings, model)
