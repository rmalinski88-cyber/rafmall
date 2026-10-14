"""Trela's universe: every US listing (ADRs included) with a market cap of 10 bn USD+.

Trela's final model works on US exchanges only ("lepsze prognozy analityków;
w teście podniosło wynik"), with a loose screener in front and the rigour in
the model.  The list comes from TradingView's public screener - one request
instead of a ticker file to keep up to date - and falls back to the US part
of the humanoid list when that unofficial endpoint fails, so a run never
silently scores nothing.

Companies from ``data/universe_humanoid_global.csv`` are tagged so the
report can show where the user's theme stands in the whole market; Asian
names count through their US ADRs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from tracker.sources.tradingview import SCANNER_URL, to_yahoo

US_EXCHANGES = ("NASDAQ", "NYSE", "AMEX")
HUMANOID_LIST = "data/universe_humanoid_global.csv"

# Home listing -> US ADR on NYSE/NASDAQ.  Only exchange-listed ADRs: OTC
# receipts (FANUY, SIEGY, ...) have thin analyst coverage and Trela's
# screener does not see them.
ADR = {
    "2330.TW": "TSM",
    "6758.T": "SONY",
    "7203.T": "TM",
    "7267.T": "HMC",
    "STMPA.PA": "STM",
    "9868.HK": "XPEV",
}


def build_query(min_market_cap_usd: float, limit: int = 2000) -> dict:
    return {
        "filter": [
            {"left": "type", "operation": "in_range", "right": ["stock", "dr"]},
            {"left": "market_cap_basic", "operation": "egreater", "right": min_market_cap_usd},
            {"left": "exchange", "operation": "in_range", "right": list(US_EXCHANGES)},
        ],
        "columns": ["name", "description", "market_cap_basic", "exchange", "Value.Traded"],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "range": [0, limit],
    }


def parse_rows(payload: dict, min_market_cap_usd: float = 0.0) -> pd.DataFrame:
    """One row per company: share classes collapse to the most traded line."""
    rows = []
    for item in payload.get("data", []) or []:
        d = item.get("d") or []
        symbol = item.get("s", "")
        if len(d) < 4 or ":" not in symbol:
            continue
        exchange, ticker = symbol.split(":", 1)
        # `markets`/exchange filters have leaked OTC rows before; check again here.
        if exchange not in US_EXCHANGES or "/" in ticker:
            continue
        cap = d[2]
        if cap is None or cap < min_market_cap_usd:
            continue
        rows.append({
            "ticker": to_yahoo(ticker, exchange),
            "name": d[1] or ticker,
            "exchange": exchange,
            "market_cap_usd": float(cap),
            "traded": float(d[4] or 0.0) if len(d) > 4 else 0.0,
        })
    if not rows:
        return pd.DataFrame(columns=["ticker", "name", "exchange", "market_cap_usd"])
    frame = pd.DataFrame(rows)
    # GOOGL/GOOG, BRK.A/BRK.B: same company, same market cap - Trela removes
    # these duplicates by hand; keep the line people actually trade.
    frame["key"] = frame["name"].str.lower().str.strip()
    frame = frame.sort_values("traded", ascending=False).drop_duplicates("key")
    frame = frame.sort_values("market_cap_usd", ascending=False)
    return frame.drop(columns=["key", "traded"]).reset_index(drop=True)


def fetch_us_universe(min_market_cap_usd: float = 10e9, timeout: int = 30) -> pd.DataFrame:
    """US listings above the cap from TradingView; raises on transport error."""
    import requests

    response = requests.post(
        SCANNER_URL.format(market="america"), json=build_query(min_market_cap_usd), timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    response.raise_for_status()
    return parse_rows(response.json(), min_market_cap_usd)


def humanoid_tickers(path: str | Path = HUMANOID_LIST) -> set[str]:
    """US symbols of the user's humanoid-robotics companies (home US listings + ADRs)."""
    try:
        frame = pd.read_csv(path, comment="#")
    except (OSError, ValueError):
        return set()
    out = set()
    for ticker in frame["ticker"].dropna().astype(str):
        if ticker in ADR:
            out.add(ADR[ticker])
        elif "." not in ticker:
            out.add(ticker)
    return out


def us_universe(min_market_cap_usd: float = 10e9, fetch=fetch_us_universe,
                humanoids: set[str] | None = None) -> tuple[pd.DataFrame, str]:
    """``(universe with a 'humanoid' column, description of the source)``."""
    humanoids = humanoid_tickers() if humanoids is None else humanoids
    try:
        frame = fetch(min_market_cap_usd)
        source = f"TradingView: giełdy USA, kapitalizacja ≥ {min_market_cap_usd / 1e9:g} mld USD"
    except Exception as exc:  # noqa: BLE001 - unofficial endpoint; fall back, but say so
        frame = pd.DataFrame(columns=["ticker", "name"])
        source = f"TradingView niedostępny ({exc.__class__.__name__})"
    if frame.empty:
        frame = pd.DataFrame({"ticker": sorted(humanoids), "name": sorted(humanoids)})
        source += " — ZAPASOWO tylko spółki humanoidalne z USA"
    else:
        # A humanoid name under the cap still belongs in the user's view; the
        # model's own must-have flags it.
        missing = sorted(humanoids - set(frame["ticker"]))
        if missing:
            frame = pd.concat([frame, pd.DataFrame({"ticker": missing, "name": missing})], ignore_index=True)
    frame["humanoid"] = frame["ticker"].isin(humanoids)
    return frame.reset_index(drop=True), source
