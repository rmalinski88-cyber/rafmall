"""TradingView as a second source of analyst price targets (no network)."""

from __future__ import annotations

import pandas as pd
import pytest

from screener.providers.tradingview import TradingViewProvider
from screener.trela.data import Readings
from screener.trela.targets import TargetHistory, TradingViewTargets, symbol_candidates


def _transport(rows):
    def send(url, payload, timeout):
        wanted = payload["columns"]
        data = [{"s": sym, "d": [rows[sym].get(c) for c in wanted]}
                for sym in payload["symbols"]["tickers"] if sym in rows]
        return 200, {"data": data}
    return send


def test_symbols_for_asian_and_us_tickers():
    assert symbol_candidates("6324.T") == ["TSE:6324"]
    assert symbol_candidates("NVDA", "NASDAQ") == ["NASDAQ:NVDA"]
    assert symbol_candidates("BRK-B") == ["NASDAQ:BRK.B", "NYSE:BRK.B", "AMEX:BRK.B"]


def test_history_keeps_one_snapshot_per_day(tmp_path):
    history = TargetHistory(tmp_path / "h.csv")
    history.record("2026-10-01", {"6324.T": (5000.0, 4000.0)})
    history.record("2026-10-01", {"6324.T": (5100.0, 4000.0)})
    history.record("2026-10-02", {"6324.T": (5200.0, 4100.0)})
    history.save()
    again = TargetHistory(tmp_path / "h.csv")
    assert list(again.series("6324.T")) == [5100.0, 5200.0]


def test_asian_listing_gets_upside_and_drawdown_from_tradingview(tmp_path):
    history = TargetHistory(tmp_path / "h.csv")
    for day, target in (("2026-09-10", 5000.0), ("2026-09-20", 5000.0), ("2026-10-01", 4500.0)):
        history.record(day, {"6324.T": (target, 4000.0)})
    provider = TradingViewProvider(transport=_transport(
        {"TSE:6324": {"close": 4000.0, "price_target_average": 4500.0}}))
    targets = TradingViewTargets(history, provider=provider, today="2026-10-14")
    assert targets.prefetch(["6324.T"]) == 1

    r = Readings("6324.T", values={"altman": 3.0, "pt_change_180d": None, "pt_drawdown_45d": None,
                                   "upside_vs_history": None})
    targets.fill(r)
    assert r.upside_now == pytest.approx(0.125)
    assert r.values["pt_drawdown_45d"] == pytest.approx(-0.10)     # 5000 -> 4500: a real cut, flags
    assert r.values["pt_change_180d"] is None                      # history too short
    assert "TradingView" in r.notes[-1]


def test_yahoo_history_is_not_overwritten(tmp_path):
    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"),
                                 provider=TradingViewProvider(transport=_transport({})))
    r = Readings("NVDA", values={"pt_change_180d": 0.2, "pt_drawdown_45d": 0.0, "upside_vs_history": 0.5})
    assert targets.fill(r).values["pt_change_180d"] == 0.2


def test_rejected_target_column_is_reported(tmp_path):
    def send(url, payload, timeout):
        if "price_target_1y" in payload["columns"]:
            return 400, "Unknown field price_target_1y"
        return 200, {"data": [{"s": "TSE:6324", "d": [4000.0 if c == "close" else (4800.0 if c == "price_target_average" else None)
                                                    for c in payload["columns"]]}]}

    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"), provider=TradingViewProvider(transport=send))
    assert targets.prefetch(["6324.T"]) == 1
    assert any("price_target_1y" in n for n in targets.notes)


def test_unreachable_tradingview_does_not_stop_the_run(tmp_path):
    def broken(url, payload, timeout):
        raise ConnectionError("blocked")

    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"), provider=TradingViewProvider(transport=broken))
    assert targets.prefetch(["6324.T"]) == 0 and targets.notes
    r = Readings("6324.T", values={"altman": 3.0})
    assert targets.fill(r) is r and r.upside_now is None


def test_target_in_usd_is_converted_to_the_listing_currency(tmp_path):
    rows = {
        "TWSE:2330": {"close": 2490.0, "currency": "TWD", "fundamental_currency_code": "USD",
                      "price_target_average": 104.4},
        "FX_IDC:USDTWD": {"close": 31.6},
        "TSE:6324": {"close": 4000.0, "currency": "JPY", "fundamental_currency_code": "USD",
                     "price_target_average": 50.0},     # no USDJPY quote: cannot convert
    }
    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"), provider=TradingViewProvider(transport=_transport(rows)))
    assert targets.prefetch(["2330.TW", "6324.T"]) == 1
    assert targets.snapshot["2330.TW"]["target"] == pytest.approx(104.4 * 31.6)
    assert any("6324.T" in n for n in targets.notes)


def test_implausible_upside_is_dropped(tmp_path):
    rows = {"TSE:6324": {"close": 4000.0, "currency": "JPY", "price_target_average": 50.0}}
    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"), provider=TradingViewProvider(transport=_transport(rows)))
    assert targets.prefetch(["6324.T"]) == 0
    assert "jednostki" in targets.notes[-1]


def test_rerun_on_the_same_day_drops_a_rejected_snapshot(tmp_path):
    history = TargetHistory(tmp_path / "h.csv")
    history.record("2026-10-14", {"6324.T": (50.0, 4000.0)})        # stored before the unit fix
    rows = {"TSE:6324": {"close": 4000.0, "currency": "JPY", "price_target_average": 50.0}}
    TradingViewTargets(history, provider=TradingViewProvider(transport=_transport(rows)),
                       today="2026-10-14").prefetch(["6324.T"])
    assert history.series("6324.T").empty


def test_disagreeing_sources_are_named(tmp_path):
    rows = {"TSE:6324": {"close": 4000.0, "currency": "JPY", "price_target_average": 6000.0}}
    targets = TradingViewTargets(TargetHistory(tmp_path / "h.csv"), provider=TradingViewProvider(transport=_transport(rows)))
    targets.prefetch(["6324.T"])
    r = Readings("6324.T", values={"altman": 3.0}, price_target=4400.0)
    targets.fill(r)
    assert r.upside_now == pytest.approx(0.5)
    assert any("Yahoo 4 400.00" in n and "TradingView 6 000.00" in n for n in r.notes)
