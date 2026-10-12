"""Tracker tests: parsers on literal documents, signal maths, and the CLI end-to-end offline."""

from __future__ import annotations

from datetime import date

import pytest

from tracker.amounts import format_range, parse_range
from tracker.cli import main
from tracker.funds import diff_holdings, normalise_name, resolve_tickers
from tracker.instruments import CRYPTO, ETF, STOCK, asset_class, normalise_symbol
from tracker.models import ADD, BUY, EXIT, HOLD, NEW, SELL, TRIM, Fund, FundReport, Holding, Trade
from tracker.signals import build_signals, label_for
from tracker.sources.quiver import parse_congress_rows
from tracker.sources.sec import parse_form4, parse_info_table, select_filings
from tracker.state import SeenStore

FORM4 = """<?xml version="1.0"?>
<ownershipDocument>
  <issuer><issuerCik>1045810</issuerCik><issuerTradingSymbol>NVDA</issuerTradingSymbol></issuer>
  <reportingOwner>
    <reportingOwnerId><rptOwnerName>Huang Jen Hsun</rptOwnerName></reportingOwnerId>
    <reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>1</isOfficer>
      <officerTitle>President and CEO</officerTitle></reportingOwnerRelationship>
  </reportingOwner>
  <aff10b5One>1</aff10b5One>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-09-02</value></transactionDate>
      <transactionCoding><transactionCode>S</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>1000</value></transactionShares>
        <transactionPricePerShare><value>200.5</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode></transactionAmounts>
    </nonDerivativeTransaction>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-09-02</value></transactionDate>
      <transactionCoding><transactionCode>M</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>5000</value></transactionShares></transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>"""

INFO_TABLE = """<?xml version="1.0"?>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
  <infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><cusip>037833100</cusip><value>1000</value>
    <shrsOrPrnAmt><sshPrnamt>10</sshPrnamt></shrsOrPrnAmt></infoTable>
  <infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><cusip>037833100</cusip><value>500</value>
    <shrsOrPrnAmt><sshPrnamt>5</sshPrnamt></shrsOrPrnAmt></infoTable>
  <infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><cusip>037833100</cusip><value>70</value>
    <shrsOrPrnAmt><sshPrnamt>1</sshPrnamt></shrsOrPrnAmt><putCall>Put</putCall></infoTable>
</informationTable>"""


# -- amounts -----------------------------------------------------------------


@pytest.mark.parametrize("text, expected", [
    ("$1,001 - $15,000", (1001.0, 15000.0)),
    ("$1,000,001 - $5,000,000", (1_000_001.0, 5_000_000.0)),
    ("Over $50,000,000", (50_000_000.0, None)),
    (15000, (15000.0, 15000.0)),
    ("", (None, None)),
    (None, (None, None)),
])
def test_parse_range(text, expected):
    assert parse_range(text) == expected


def test_format_range_keeps_suffix_dot():
    assert format_range(1001, 15000) == "1 tys. – 15 tys. USD"
    assert format_range(50e6, None) == "> 50 mln USD"


# -- SEC parsers -------------------------------------------------------------


def test_form4_keeps_only_open_market_trades():
    trades = parse_form4(FORM4, filed=date(2026, 9, 4))
    assert len(trades) == 1  # the option exercise (M) is mechanical, not a signal
    t = trades[0]
    assert (t.ticker, t.side, t.actor) == ("NVDA", SELL, "Huang Jen Hsun")
    assert t.amount_low == pytest.approx(200_500.0)
    assert t.planned is True
    assert "CEO" in t.role and "Director" in t.role
    assert t.lag_days == 2


def test_form4_garbage_is_empty_not_crash():
    assert parse_form4("<not xml") == []


def test_info_table_aggregates_by_cusip_and_separates_options():
    holdings = {(h.cusip, h.put_call): h for h in parse_info_table(INFO_TABLE, filed=date(2026, 8, 14))}
    assert holdings[("037833100", "")].shares == 15
    assert holdings[("037833100", "")].value == 1500
    assert holdings[("037833100", "PUT")].shares == 1


def test_info_table_pre_2023_values_were_thousands():
    holdings = parse_info_table(INFO_TABLE, filed=date(2022, 11, 14))
    assert max(h.value for h in holdings) == 1_500_000


def test_select_filings_filters_form_and_date():
    payload = {"filings": {"recent": {
        "form": ["4", "10-Q", "4", "4"],
        "accessionNumber": ["a", "b", "c", "d"],
        "filingDate": ["2026-10-01", "2026-09-30", "2026-09-01", "2026-06-01"],
        "reportDate": ["", "", "", ""],
        "primaryDocument": ["x.xml", "q.htm", "y.xml", "z.xml"],
    }}}
    got = select_filings(payload, {"4"}, since=date(2026, 8, 1), limit=10)
    assert [f["accession"] for f in got] == ["a", "c"]


# -- Quiver ------------------------------------------------------------------


def test_quiver_rows_parse_and_skip_exchanges():
    rows = [
        {"Representative": "Nancy Pelosi", "Ticker": "nvda", "Transaction": "Purchase",
         "TransactionDate": "2026-09-01", "ReportDate": "2026-09-20", "Range": "$1,000,001 - $5,000,000",
         "House": "Representatives", "Party": "D"},
        {"Representative": "X", "Ticker": "AAPL", "Transaction": "Exchange", "ReportDate": "2026-09-20"},
        {"Representative": "Y", "Ticker": "MSFT", "Transaction": "Sale (Partial)",
         "TransactionDate": "2026-01-01", "ReportDate": "2026-01-10", "Range": "$1,001 - $15,000"},
    ]
    trades, skipped = parse_congress_rows(rows, since=date(2026, 9, 1))
    assert skipped == 1
    assert len(trades) == 1  # the January sale is outside the window
    t = trades[0]
    assert (t.ticker, t.side, t.role, t.lag_days) == ("NVDA", BUY, "D-Izba", 19)


# -- 13F ---------------------------------------------------------------------


def test_diff_holdings_classifies_moves():
    prev = [Holding("A", "1", 100, 100), Holding("B", "2", 100, 100), Holding("C", "3", 100, 100),
            Holding("D", "4", 100, 100)]
    now = [Holding("A", "1", 150, 150), Holding("B", "2", 50, 50), Holding("C", "3", 102, 102),
           Holding("E", "5", 10, 10)]
    kinds = {c.cusip: c.kind for c in diff_holdings(now, prev)}
    assert kinds == {"1": ADD, "2": TRIM, "3": HOLD, "4": EXIT, "5": NEW}


def test_ticker_resolution_prefers_cusip_then_name():
    holdings = [Holding("APPLE INC", "037833100", 1, 1), Holding("MICROSOFT CORP", "X", 1, 1),
                Holding("UNKNOWN THING", "Y", 1, 1)]
    resolved = resolve_tickers(holdings, {"037833100": "AAPL"}, {normalise_name("Microsoft Corporation"): "MSFT"})
    assert [h.ticker for h in resolved] == ["AAPL", "MSFT", None]


# -- signals -----------------------------------------------------------------


def _trade(actor, side, source="congress", role="D-Izba", ticker="NVDA", planned=False):
    return Trade(source, actor, role, ticker, side, date(2026, 9, 1), date(2026, 9, 5), 1000, 15000,
                 planned=planned)


def test_each_person_counts_once_per_side():
    trades = [_trade("A", BUY), _trade("A", BUY), _trade("B", BUY)]
    [signal] = build_signals(trades, [])
    assert signal.score == 2.0
    assert signal.trades == 3


def test_ceo_purchase_outweighs_and_planned_sale_is_neutral():
    trades = [
        _trade("CEO", BUY, source="insider", role="Chief Executive Officer"),
        _trade("CFO", SELL, source="insider", role="Chief Financial Officer", planned=True),
    ]
    [signal] = build_signals(trades, [])
    assert signal.score == 3.0


def test_portfolio_alert_sorts_first():
    trades = [_trade("A", SELL, ticker="MSFT"), _trade("B", BUY, ticker="PG"), _trade("C", BUY, ticker="PG")]
    signals = build_signals(trades, [], portfolio={"MSFT"})
    assert signals[0].ticker == "MSFT" and signals[0].alert


def test_fund_changes_feed_signals_but_options_do_not():
    from tracker.models import FundChange

    fund = Fund("brk", "Berkshire", "Warren Buffett", 1)
    changes = [FundChange("APPLE", "1", "AAPL", NEW, 10, 0, 10, 0, 0.5),
               FundChange("APPLE", "1", "AAPL", NEW, 10, 0, 10, 0, 0.5, put_call="PUT")]
    report = FundReport(fund, None, None, None, 10, changes)
    [signal] = build_signals([], [report])
    assert signal.score == 2.0 and signal.buyers == {"Warren Buffett"}


@pytest.mark.parametrize("score, label", [(3, "SILNY POPYT"), (1, "POPYT"), (0, "MIESZANE"),
                                          (-1, "PODAŻ"), (-3, "SILNA PODAŻ")])
def test_labels(score, label):
    assert label_for(score) == label


# -- instruments / state -----------------------------------------------------


def test_symbol_normalisation():
    assert normalise_symbol("btc") == "BTC-USD"
    assert normalise_symbol("brk.b") == "BRK-B"
    assert normalise_symbol("7203.T") == "7203.T"


def test_asset_class():
    assert asset_class("SPY", {"quote_type": "ETF"}, set()) == ETF
    assert asset_class("ETH-USD", {}, set()) == CRYPTO
    assert asset_class("QQQ", {}, {"QQQ"}) == ETF
    assert asset_class("NVDA", {}, set()) == STOCK


def test_seen_store_round_trip(tmp_path):
    path = tmp_path / "seen.json"
    trades = [_trade("A", BUY), _trade("B", SELL)]
    store = SeenStore(path)
    assert store.new(trades) == trades
    store.remember(trades[:1])
    store.save()
    assert SeenStore(path).new(trades) == trades[1:]


def test_corrupt_state_is_a_fresh_start(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("{broken")
    assert SeenStore(path).keys == set()


# -- CLI end-to-end (offline) ------------------------------------------------


@pytest.fixture
def offline_config(tmp_path):
    src = open("config/tracker.yml", encoding="utf-8").read()
    cfg = tmp_path / "tracker.yml"
    cfg.write_text(src.replace(".cache/tracker_seen.json", str(tmp_path / "seen.json"))
                      .replace(".cache/tracker_alerts_seen.json", str(tmp_path / "alerts_seen.json"))
                      .replace(".cache/tracker_market_seen.json", str(tmp_path / "market_seen.json"))
                      .replace("cache_dir: .cache", f"cache_dir: {tmp_path / 'cache'}"), encoding="utf-8")
    return cfg


def test_scan_writes_reports_and_then_reports_nothing_new(offline_config, tmp_path, capsys):
    args = ["--config", str(offline_config), "--feed", "fixture", "--no-cache"]
    out = tmp_path / "out"
    assert main(args + ["scan", "--out-dir", str(out)]) == 0
    html = next(out.glob("tracker_*.html")).read_text(encoding="utf-8")
    assert "Sygnały według spółek" in html and "Fundusze" in html
    assert next(out.glob("signals_*.json")).stat().st_size > 0

    capsys.readouterr()
    assert main(args + ["scan", "--new-only", "--no-html", "--no-quotes", "--out-dir", str(out)]) == 0
    assert "Brak nowych transakcji" in capsys.readouterr().out


@pytest.mark.parametrize("command", [
    ["find", "nvid"], ["quote", "NVDA", "BTC", "SPY"], ["congress", "--side", "buy"],
    ["insiders", "NVDA", "AAPL"], ["funds", "berkshire"],
])
def test_commands_run_offline(offline_config, command):
    assert main(["--config", str(offline_config), "--feed", "fixture", "--no-cache", *command]) == 0


# -- alerts ----------------------------------------------------------------


def _frame(closes, volumes=None):
    import numpy as np
    import pandas as pd

    n = len(closes)
    closes = np.asarray(closes, dtype=float)
    volumes = np.asarray(volumes if volumes is not None else [1_000_000] * n, dtype=float)
    idx = pd.bdate_range(end="2026-10-09", periods=n)
    return pd.DataFrame({"open": closes, "high": closes * 1.01, "low": closes * 0.99,
                         "close": closes, "volume": volumes}, index=idx)


def test_volume_spike_alert():
    from tracker.alerts import DEFAULTS, WOLUMEN, detect

    frame = _frame([100.0] * 60, [1_000_000] * 59 + [4_000_000])
    kinds = {a.kind for a in detect("X", "X", frame, DEFAULTS)}
    assert WOLUMEN in kinds


def test_price_move_scales_with_atr():
    from tracker.alerts import DEFAULTS, RUCH, detect

    quiet = _frame([100.0] * 59 + [106.0])  # 6% on a stock whose range is ~2%/day
    kinds = {a.kind for a in detect("Q", "Q", quiet, DEFAULTS)}
    assert RUCH in kinds


def test_buy_the_dip_uses_threshold():
    from tracker.alerts import DEFAULTS, OKAZJA, detect

    import numpy as np
    closes = list(np.linspace(100, 150, 200)) + list(np.linspace(150, 110, 60))  # ~27% off the high
    frame = _frame(closes)
    assert any(a.kind == OKAZJA for a in detect("D", "D", frame, DEFAULTS, dip_threshold=20))
    assert not any(a.kind == OKAZJA for a in detect("D", "D", frame, DEFAULTS, dip_threshold=40)
                   if "poniżej SMA200" not in a.detail)


def test_quiet_stock_raises_nothing():
    from tracker.alerts import DEFAULTS, detect

    import numpy as np
    rng = np.random.default_rng(1)
    closes = 100 + np.cumsum(rng.normal(0, 0.3, 300))
    frame = _frame(closes)
    kinds = {a.kind for a in detect("Z", "Z", frame, DEFAULTS)}
    assert "wolumen" not in kinds and "ruch" not in kinds


def test_discord_chunking_respects_limit():
    from tracker.notify import chunk

    text = "\n".join(f"line {i} " + "x" * 80 for i in range(100))
    parts = chunk(text, limit=500)
    assert all(len(p) <= 500 for p in parts) and "".join(parts).count("line") == 100


def test_alerts_command_reports_only_new_on_second_run(offline_config, tmp_path, capsys):
    args = ["--config", str(offline_config), "--feed", "fixture", "--no-cache"]
    assert main(args + ["alerts", "--no-smart", "--out-dir", str(tmp_path)]) == 0
    first = capsys.readouterr().out
    assert "nowych" in first and next(tmp_path.glob("alerts_*.json")).stat().st_size > 0
    assert main(args + ["alerts", "--no-smart", "--out-dir", str(tmp_path)]) == 0
    assert "0 nowych" in capsys.readouterr().out


def test_swing_levels_expire_once_broken():
    from tracker.alerts import swing_levels

    import numpy as np
    # a clear peak at bar 30, then price stays below it: the level is live
    closes = np.array([100.0] * 30 + [120.0] + [100.0] * 40)
    frame = _frame(closes)
    frame.loc[frame.index[30], "high"] = 121.0
    live = swing_levels(frame, window=5, lookback=90)
    assert any(abs(level - 121.0) < 1e-9 and side == "high" for level, side in live)
    # once a later close exceeds it, it is spent
    closes2 = closes.copy(); closes2[60:] = 125.0
    frame2 = _frame(closes2); frame2.loc[frame2.index[30], "high"] = 121.0
    assert not any(abs(level - 121.0) < 1e-9 for level, _ in swing_levels(frame2, 5, 90))


def test_confluence_needs_two_kinds():
    from tracker.alerts import KONFLUENCJA, Alert, mark_confluence
    from datetime import date

    d = date(2026, 10, 9)
    one = [Alert("wolumen", "X", "X", "a", "b", 3.0, day=d)]
    assert not any(a.kind == KONFLUENCJA for a in mark_confluence(one))
    two = one + [Alert("poziom", "X", "X", "c", "d", 1.8, day=d)]
    out = mark_confluence(two)
    assert any(a.kind == KONFLUENCJA and a.score > 10 for a in out)


# -- market scan -------------------------------------------------------------


def _ema_setup_frame(hold=3, vol_mult=3.0, pre=80):
    """Flat below EMA, then a break with volume, then `hold` closes above."""
    import numpy as np
    closes = [100.0 - 0.1 * i for i in range(pre)]            # drifting down: below EMA
    closes += [108.0] + [109.0 + i for i in range(hold - 1)]  # break + hold
    vols = [1_000_000] * pre + [int(1_000_000 * vol_mult)] + [1_200_000] * (hold - 1)
    return _frame(closes, vols)


def test_ema30_fires_after_three_day_hold_with_volume():
    from tracker.market import DEFAULTS, ema_break_and_hold

    hit = ema_break_and_hold("T", "Test", _ema_setup_frame(), DEFAULTS)
    assert hit is not None and "od 3 sesji" in hit.headline and "3.0×" in hit.headline


def test_ema30_needs_volume_and_hold():
    from tracker.market import DEFAULTS, ema_break_and_hold

    assert ema_break_and_hold("T", "T", _ema_setup_frame(vol_mult=1.2), DEFAULTS) is None
    assert ema_break_and_hold("T", "T", _ema_setup_frame(hold=2), DEFAULTS) is None


def test_ema30_ignores_old_breaks():
    from tracker.market import DEFAULTS, ema_break_and_hold

    assert ema_break_and_hold("T", "T", _ema_setup_frame(hold=10), DEFAULTS) is None


def test_liquidity_floor():
    from tracker.market import DEFAULTS, liquid_enough

    assert liquid_enough(_frame([50.0] * 80, [100_000] * 80), DEFAULTS)
    assert not liquid_enough(_frame([1.0] * 80, [100_000] * 80), DEFAULTS)  # penny
    assert not liquid_enough(_frame([50.0] * 80, [1_000] * 80), DEFAULTS)   # thin


def test_market_command_runs_on_symbol_file(offline_config, tmp_path, capsys):
    symbols = tmp_path / "s.csv"
    symbols.write_text("ticker,name\nNVDA,NVIDIA\nMSFT,Microsoft\nAAPL,Apple\n", encoding="utf-8")
    args = ["--config", str(offline_config), "--feed", "fixture", "--no-cache",
            "market", "--symbols", str(symbols), "--all", "--out-dir", str(tmp_path)]
    assert main(args) == 0
    assert "Skan rynku" in capsys.readouterr().out
    assert next(tmp_path.glob("market_*.json")).exists()


def test_tradingview_query_and_parse():
    from tracker.sources.tradingview import build_query, parse_response, to_yahoo

    q = build_query(2.0, 30, 2.0, 2_000_000, exchanges=["NASDAQ"])
    assert any(f["left"] == "EMA30" for f in q["filter"]) and q["markets"] == ["NASDAQ"]
    payload = {"data": [{"s": "NASDAQ:NVDA", "d": ["NVDA", "NVIDIA", 190.0, 5e7, 2.4]},
                        {"s": "XETR:SIE", "d": ["SIE", "Siemens", 180.0, 1e6, 2.1]},
                        {"s": "garbage", "d": []}]}
    rows = parse_response(payload)
    assert [r["ticker"] for r in rows] == ["NVDA", "SIE"]
    assert to_yahoo("SIE", "XETR") == "SIE.DE" and to_yahoo("BRK.B", "NYSE") == "BRK-B"
    assert parse_response({"unexpected": 1}) == []


def _arb_like_frame():
    """Impulse through EMA on volume, 3-bar correction to the EMA, then an up-close."""
    import numpy as np
    base = [0.090 - 0.0002 * i for i in range(80)]                      # slow drift down: below EMA
    impulse = [0.086, 0.094, 0.100]                                      # three strong up bars
    correction = [0.094, 0.088, 0.084]                                   # back to the (now rising) EMA
    entry = [0.088]
    closes = base + impulse + correction + entry
    vols = [10e6] * 80 + [35e6, 40e6, 30e6] + [15e6, 12e6, 11e6] + [14e6]
    frame = _frame(closes, vols)
    # widen the impulse bars' ranges so they clear the ATR gate
    for i in range(80, 83):
        frame.loc[frame.index[i], "high"] = closes[i] * 1.06
        frame.loc[frame.index[i], "low"] = closes[i] * 0.95
    return frame


def test_pullback_entry_fires_on_arb_like_setup():
    from tracker.market import DEFAULTS, ema_pullback_entry

    hit = ema_pullback_entry("ARB-USD", "Arbitrum", _arb_like_frame(), DEFAULTS)
    assert hit is not None and hit.rule == "pullback"
    assert "korekcie" in hit.headline


def test_pullback_needs_a_correction_not_just_a_runup():
    from tracker.market import DEFAULTS, ema_pullback_entry

    frame = _arb_like_frame()
    # replace the correction with a continued run-up: no touch of the EMA zone
    import numpy as np
    idx = frame.index
    for i, v in zip(range(83, 87), [0.108, 0.112, 0.115, 0.118]):
        frame.loc[idx[i], ["open", "close"]] = v
        frame.loc[idx[i], "high"] = v * 1.01
        frame.loc[idx[i], "low"] = v * 0.99
    assert ema_pullback_entry("X", "X", frame, DEFAULTS) is None


def test_tradingview_crypto_symbol_mapping():
    from tracker.sources.tradingview import to_yahoo

    assert to_yahoo("ARBUSDT", "BINANCE") == "ARB-USD"
    assert to_yahoo("BTCUSD", "COINBASE") == "BTC-USD"


# -- env / replay ------------------------------------------------------------


def test_dotenv_sets_missing_only(tmp_path, monkeypatch):
    from tracker.env import load_dotenv

    env = tmp_path / ".env"
    env.write_text('A_TEST_KEY="hello world"\n# comment\nexport B_TEST_KEY=1\nC_TEST_KEY=keep\n', encoding="utf-8")
    monkeypatch.setenv("C_TEST_KEY", "already")
    monkeypatch.delenv("A_TEST_KEY", raising=False)
    monkeypatch.delenv("B_TEST_KEY", raising=False)
    assert load_dotenv(env) == 2
    import os
    assert os.environ["A_TEST_KEY"] == "hello world" and os.environ["B_TEST_KEY"] == "1"
    assert os.environ["C_TEST_KEY"] == "already"


def test_replay_command_runs_offline(offline_config, capsys):
    assert main(["--config", str(offline_config), "--feed", "fixture", "--no-cache",
                 "replay", "ARB", "--rule", "pullback", "--days", "60"]) == 0
    out = capsys.readouterr().out
    assert "ARB-USD" in out and "reguła pullback" in out


def test_pullback_fires_once_per_setup():
    """After the entry bar, more up-closes must not re-trigger the same setup."""
    from tracker.market import DEFAULTS, ema_pullback_entry

    frame = _arb_like_frame()
    assert ema_pullback_entry("A", "A", frame, DEFAULTS) is not None
    import pandas as pd
    nxt = frame.iloc[-1].copy()
    nxt[["open", "close"]] = frame["close"].iloc[-1] * 1.02
    nxt["high"], nxt["low"] = nxt["close"] * 1.01, nxt["close"] * 0.99
    frame2 = pd.concat([frame, pd.DataFrame([nxt], index=[frame.index[-1] + pd.offsets.BDay()])])
    assert ema_pullback_entry("A", "A", frame2, DEFAULTS) is None


def test_live_feed_without_sec_user_agent_degrades_gracefully(monkeypatch):
    from datetime import date
    from tracker.sources.live import LiveFeed

    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    feed = LiveFeed({}, fresh_cache=None, archive_cache=None)   # must not raise
    assert feed.insider_trades("NVDA", date(2026, 1, 1)) == []
    assert feed.all_names() == [] and feed.search_names("nvda") == []
    assert len(feed.warnings) == 1 and "SEC" in feed.warnings[0]
