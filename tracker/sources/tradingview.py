"""TradingView screener as a candidate source for the market scan.

TradingView has no official data API.  Its web screener, however, is fed by a
public, login-free JSON endpoint, and asking it "which symbols have volume
2x their average and close above EMA30" is one request instead of thousands
of price downloads.  It is unofficial: it can change without notice, so the
caller must treat an empty or failing answer as "fall back to the SEC list",
never as "nothing matches".

Only the pre-filter happens here.  The 3-day hold and everything else is
confirmed on our own price data afterwards.
"""

from __future__ import annotations

SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"

# Market slug -> TradingView exchanges included.  "global" is their all-markets slug.
MARKETS = {
    "america": ["NASDAQ", "NYSE", "AMEX"],
    "global": [],
    "germany": ["XETR", "FWB"],
    "japan": ["TSE"],
    "poland": ["GPW"],
    "crypto": [],  # TradingView's crypto screener slug; pairs like BINANCE:ARBUSDT
}


def build_query(volume_multiple: float, ema_len: int, min_price: float,
                min_dollar_volume: float, limit: int = 500, exchanges: list[str] | None = None) -> dict:
    """The screener's JSON body for 'volume spike + close above EMA'."""
    crypto = exchanges is not None and market_is_crypto(exchanges)
    filters = [] if crypto else [
        {"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]},
    ]
    filters += [
        {"left": "close", "operation": "greater", "right": min_price},
        {"left": f"EMA{ema_len}", "operation": "less", "right": "close"},
        {"left": "relative_volume_10d_calc", "operation": "greater", "right": volume_multiple},
        {"left": "Value.Traded", "operation": "greater", "right": min_dollar_volume},
    ]
    query: dict = {
        "filter": filters,
        "columns": ["name", "description", "close", "volume", "relative_volume_10d_calc",
                    f"EMA{ema_len}", "Value.Traded", "exchange"],
        "sort": {"sortBy": "relative_volume_10d_calc", "sortOrder": "desc"},
        "range": [0, limit],
    }
    if exchanges and not crypto:
        query["markets"] = exchanges
    return query


def market_is_crypto(exchanges) -> bool:
    return exchanges == ["__crypto__"]


def parse_response(payload: dict) -> list[dict]:
    """Rows as dicts; a shape we do not recognise yields [] rather than garbage."""
    rows = []
    for item in payload.get("data", []) or []:
        d = item.get("d") or []
        symbol = item.get("s", "")
        if len(d) < 3 or ":" not in symbol:
            continue
        exchange, ticker = symbol.split(":", 1)
        rows.append({
            "ticker": ticker, "name": d[1] or ticker, "exchange": exchange,
            "close": d[2], "volume": d[3] if len(d) > 3 else None,
            "relative_volume": d[4] if len(d) > 4 else None,
        })
    return rows


def to_yahoo(ticker: str, exchange: str) -> str:
    """TradingView 'XETR:SIE' -> Yahoo 'SIE.DE'; 'BINANCE:ARBUSDT' -> 'ARB-USD'; US tickers pass through."""
    if exchange in ("BINANCE", "COINBASE", "BYBIT", "OKX", "KRAKEN", "BITGET", "KUCOIN", "CRYPTO"):
        base = ticker
        for quote in ("USDT", "USDC", "USD", "BUSD"):
            if base.endswith(quote):
                base = base[: -len(quote)]
                break
        return f"{base}-USD"
    suffix = {"XETR": ".DE", "FWB": ".F", "TSE": ".T", "GPW": ".WA", "LSE": ".L", "EURONEXT": ".PA",
              "SIX": ".SW", "HKEX": ".HK", "TWSE": ".TW", "KRX": ".KS", "SSE": ".SS", "SZSE": ".SZ"}.get(exchange, "")
    return ticker.replace(".", "-") + suffix


def fetch_candidates(market: str, volume_multiple: float, ema_len: int, min_price: float,
                     min_dollar_volume: float, limit: int = 500, timeout: int = 30) -> list[tuple[str, str]]:
    """``(yahoo_symbol, name)`` for every screener hit; raises on transport error."""
    import requests

    exchanges = ["__crypto__"] if market == "crypto" else MARKETS.get(market)
    query = build_query(volume_multiple, ema_len, min_price if market != "crypto" else 0.0,
                        min_dollar_volume, limit, exchanges)
    if market == "crypto":
        query.pop("markets", None)
        # The first live run returned 0 rows with a `currency` filter; narrow by exchange and
        # pair name instead. One row per coin across exchanges comes later via to_yahoo dedupe.
        query["filter"].append({"left": "exchange", "operation": "in_range",
                                "right": ["BINANCE", "COINBASE", "BYBIT", "OKX", "KRAKEN"]})
        query["filter"].append({"left": "name", "operation": "match", "right": "(USDT|USD)$"})
    response = requests.post(SCANNER_URL.format(market=market), json=query, timeout=timeout,
                             headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    response.raise_for_status()
    rows = parse_response(response.json())
    seen: dict[str, str] = {}
    for r in rows:
        seen.setdefault(to_yahoo(r["ticker"], r["exchange"]), r["name"])
    return list(seen.items())
