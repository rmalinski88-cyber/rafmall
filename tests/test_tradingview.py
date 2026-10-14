"""TradingView provider tests, driven by a fake transport.

The real endpoint is unreachable from the test environment and would be a
flaky dependency anyway; the transport is the one seam, so everything above
it - symbol mapping, bulk fetching, percent handling, currency conversion,
field-rejection retries, caching, the pipeline integration - runs here
against canned answers shaped exactly like the screener's JSON.
"""

from __future__ import annotations

import zlib

import pandas as pd
import pytest

from screener.cache import Cache
from screener.config import load_config
from screener.pipeline import run_screen
from screener.providers import get_provider
from screener.providers.base import ProviderError
from screener.providers.tradingview import (
    ALL_COLUMNS,
    TradingViewProvider,
    fx_symbol,
    to_tradingview,
)
from screener.universe import load_universe

PCT_COLUMNS = {
    "total_revenue_yoy_growth_ttm", "net_income_yoy_growth_ttm", "gross_margin_ttm",
    "operating_margin_ttm", "net_margin_ttm", "return_on_equity", "return_on_assets",
    "Perf.1M", "Perf.3M", "Perf.6M", "Perf.Y",
}
CURRENCY_BY_EXCHANGE = {
    "TSE": "JPY", "KRX": "KRW", "TWSE": "TWD", "TPEX": "TWD",
    "HKEX": "HKD", "SSE": "CNY", "SZSE": "CNY", "TVC": "JPY", "HSI": "HKD",
}
FX_PER_USD = {"USDJPY": 150.0, "USDKRW": 1400.0, "USDTWD": 32.0, "USDHKD": 7.8, "USDCNY": 7.2}


def _seed(symbol: str, column: str) -> float:
    return (zlib.crc32(f"{symbol}|{column}".encode()) % 1000) / 1000.0


def value_for(symbol: str, column: str):
    exchange = symbol.split(":")[0]
    if symbol.startswith("FX_IDC:"):
        return FX_PER_USD.get(symbol.split(":")[1]) if column == "close" else None
    if column == "description":
        return f"Spółka {symbol}"
    if column == "sector":
        return "Industrials"
    if column == "industry":
        return "Robotics"
    if column == "currency":
        return CURRENCY_BY_EXCHANGE[exchange]
    if column == "fundamental_currency_code":
        return "CNY" if exchange == "HKEX" else CURRENCY_BY_EXCHANGE[exchange]
    if column == "type":
        return "index" if exchange in ("TVC", "HSI") or symbol.endswith(":KOSPI") else "stock"
    seed = _seed(symbol, column)
    if column == "close":
        return 100.0 + seed * 50
    if column == "SMA50":
        return 100.0 + seed * 40
    if column == "SMA200":
        return 95.0 + seed * 40
    if column == "price_52_week_high":
        return 200.0
    if column == "price_52_week_low":
        return 50.0
    if column == "RSI":
        return 30.0 + seed * 40
    if column in PCT_COLUMNS:
        return -20.0 + seed * 80  # percent scale, as TradingView reports it
    if column == "market_cap_basic":
        return 1e9 + seed * 5e12
    if column in ("volume", "average_volume_30d_calc", "average_volume_90d_calc"):
        return 2e6 + seed * 8e6  # liquid enough to clear the turnover filter
    return 1.0 + seed * 10


def make_transport(missing=(), reject=None, calls=None):
    """A stand-in for ``requests.post`` against the screener endpoint."""
    calls = calls if calls is not None else []

    def transport(url, payload, timeout):
        calls.append(payload)
        columns = payload["columns"]
        if reject and reject in columns:
            return 400, {"error": f"unknown field: {reject}"}
        data = [
            {"s": s, "d": [value_for(s, c) for c in columns]}
            for s in payload["symbols"]["tickers"]
            if s not in missing
        ]
        return 200, {"totalCount": len(data), "data": data}

    transport.calls = calls
    return transport


@pytest.fixture(scope="module")
def config():
    return load_config("config/default.yml")


@pytest.fixture(scope="module")
def universe():
    return load_universe("data/universe_humanoid_asia.csv")


# -- symbol mapping ----------------------------------------------------------


def test_symbol_mapping_covers_every_asian_board():
    assert to_tradingview("6324.T") == "TSE:6324"
    assert to_tradingview("005930.KS") == "KRX:005930"
    assert to_tradingview("277810.KQ") == "KRX:277810"
    assert to_tradingview("2330.TW") == "TWSE:2330"
    assert to_tradingview("1234.TWO") == "TPEX:1234"
    assert to_tradingview("688017.SS") == "SSE:688017"
    assert to_tradingview("300124.SZ") == "SZSE:300124"


def test_hong_kong_tickers_lose_their_leading_zeros():
    assert to_tradingview("0020.HK") == "HKEX:20"
    assert to_tradingview("9880.HK") == "HKEX:9880"


def test_explicit_and_index_symbols_pass_through():
    assert to_tradingview("NASDAQ:NVDA") == "NASDAQ:NVDA"
    assert to_tradingview("^N225") == "TVC:NI225"
    assert to_tradingview("^HSI") == "HSI:HSI"
    assert fx_symbol("jpy") == "FX_IDC:USDJPY"


def test_registry_exposes_the_provider():
    assert isinstance(get_provider("tradingview"), TradingViewProvider)


# -- fetching ---------------------------------------------------------------


def test_prefetch_asks_once_for_all_symbols_and_once_for_fx(universe):
    transport = make_transport()
    provider = TradingViewProvider(transport=transport)
    tickers = list(universe["ticker"])
    provider.prefetch([*tickers, "^N225", "^KS11"])

    assert len(transport.calls) == 2
    first, second = transport.calls
    assert len(first["symbols"]["tickers"]) == len(tickers) + 2
    assert first["columns"] == ALL_COLUMNS
    assert all(s.startswith("FX_IDC:USD") for s in second["symbols"]["tickers"])
    assert second["columns"] == ["close"]


def test_percent_fields_become_fractions():
    provider = TradingViewProvider(transport=make_transport())
    fundamentals = provider.get_fundamentals("6324.T")

    raw = value_for("TSE:6324", "total_revenue_yoy_growth_ttm")
    assert fundamentals["revenue_growth"] == pytest.approx(raw / 100.0)
    assert fundamentals["currency"] == "JPY"
    assert fundamentals["name"] == "Spółka TSE:6324"
    assert fundamentals["debt_to_equity"] == pytest.approx(value_for("TSE:6324", "debt_to_equity_fq"))


def test_technicals_are_derived_from_tradingview_indicators():
    provider = TradingViewProvider(transport=make_transport())
    metrics = provider.get_technicals("2330.TW")

    close, sma50 = value_for("TWSE:2330", "close"), value_for("TWSE:2330", "SMA50")
    assert metrics["last_close"] == pytest.approx(close)
    assert metrics["px_vs_sma50"] == pytest.approx(close / sma50 - 1.0)
    assert metrics["ret_6m"] == pytest.approx(value_for("TWSE:2330", "Perf.6M") / 100.0)
    assert 0.0 <= metrics["pos_52w_range"] <= 1.0
    assert metrics["bars"] is None
    assert metrics["max_drawdown_12m"] is None


def test_fx_rates_are_usd_per_unit_of_currency():
    provider = TradingViewProvider(transport=make_transport())
    provider.prefetch(["6324.T"])
    assert provider.get_fx_to_usd("JPY") == pytest.approx(1 / 150.0)
    assert provider.get_fx_to_usd("USD") == 1.0


def test_reporting_currency_is_converted_to_listing_currency():
    # HKEX listing, books in CNY: amounts must arrive in HKD so that
    # net_cash / market_cap compares like with like.
    provider = TradingViewProvider(transport=make_transport())
    fundamentals = provider.get_fundamentals("9880.HK")

    raw_revenue = value_for("HKEX:9880", "total_revenue_ttm")
    cny_to_hkd = (1 / 7.2) / (1 / 7.8)
    assert fundamentals["total_revenue"] == pytest.approx(raw_revenue * cny_to_hkd)
    assert fundamentals["market_cap"] == pytest.approx(value_for("HKEX:9880", "market_cap_basic"))


def test_rejected_field_is_dropped_reported_and_the_request_retried():
    transport = make_transport(reject="gross_margin_ttm")
    provider = TradingViewProvider(transport=transport)
    fundamentals = provider.get_fundamentals("6324.T")

    assert "gross_margin_ttm" in provider.dropped_columns
    assert fundamentals["gross_margin"] is None
    assert fundamentals["operating_margin"] is not None
    assert any("gross_margin_ttm" in note for note in provider.diagnostics())
    # rejected request, successful retry, FX lookup
    assert len(transport.calls) == 3


def test_missing_symbol_is_reported_not_invented():
    provider = TradingViewProvider(transport=make_transport(missing={"KRX:056080"}))
    provider.prefetch(["056080.KQ", "6324.T"])

    assert provider.get_fundamentals("056080.KQ") == {}
    assert provider.get_technicals("056080.KQ") is None
    assert any("KRX:056080" in note for note in provider.diagnostics())


def test_transport_failure_raises_a_provider_error():
    def broken(url, payload, timeout):
        return 503, "Service Unavailable"

    with pytest.raises(ProviderError, match="503"):
        TradingViewProvider(transport=broken).get_fundamentals("6324.T")


def test_prices_are_always_empty():
    frame = TradingViewProvider(transport=make_transport()).get_prices("6324.T", 400)
    assert isinstance(frame, pd.DataFrame) and frame.empty


def test_cache_serves_a_second_provider_without_the_network(tmp_path):
    cache = Cache(tmp_path, ttl_hours=12)
    first = make_transport()
    TradingViewProvider(cache=cache, transport=first).prefetch(["6324.T", "2330.TW"])
    assert len(first.calls) == 2

    second = make_transport()
    provider = TradingViewProvider(cache=cache, transport=second)
    provider.prefetch(["6324.T", "2330.TW"])
    assert second.calls == []
    assert provider.get_fundamentals("2330.TW")["currency"] == "TWD"


# -- pipeline ---------------------------------------------------------------


def test_screen_runs_end_to_end_on_tradingview(universe, config):
    provider = TradingViewProvider(transport=make_transport())
    result = run_screen(universe, provider, config, profile_name="growth")

    assert not result.ranked.empty
    assert not result.rejected["excluded_reason"].astype(str).str.contains("cenowych").any()
    # No price history, so no sparklines - but the technical score exists.
    assert result.prices == {}
    assert result.ranked["technical_score"].notna().all()
    # Relative strength comes from the index's own performance figures.
    assert result.ranked["rs_6m"].notna().any()
    assert result.ranked["bars"].isna().all()
