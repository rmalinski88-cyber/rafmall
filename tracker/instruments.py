"""Stocks, ETFs and crypto: one quote card per symbol.

Prices come from the screener's provider layer (Yahoo by default), so the
same technical indicators - trend, RSI, returns, relative strength - apply to
all three asset classes.  Crypto is benchmarked against Bitcoin, everything
else against the S&P 500 (SPY).
"""

from __future__ import annotations

from screener.analysis.technical import compute_technical_metrics

STOCK, ETF, CRYPTO = "akcja", "ETF", "krypto"

# Bare crypto symbols people type; Yahoo quotes them as "<SYM>-USD".
CRYPTO_ALIASES = {
    "BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "AVAX", "DOT", "LINK",
    "LTC", "TRX", "TON", "SHIB", "MATIC", "POL", "SUI", "NEAR", "ATOM", "UNI",
    "ARB", "OP", "APT", "INJ", "TIA", "SEI", "RENDER", "FET", "TAO", "HBAR", "XLM", "PEPE",
}

# Coins whose ticker collides with another asset carry a numeric id in Yahoo's symbol.
# Yahoo's plain "ARB-USD" is a dead token, not Arbitrum (found on the first real dump).
CRYPTO_YAHOO = {"ARB": "ARB11841-USD", "SUI": "SUI20947-USD", "UNI": "UNI7083-USD", "APT": "APT21794-USD",
                "TAO": "TAO22974-USD", "POL": "POL28321-USD", "MATIC": "POL28321-USD",
                "TON": "TON11419-USD", "TIA": "TIA22861-USD"}

_QUOTE_TYPES = {"EQUITY": STOCK, "ETF": ETF, "MUTUALFUND": ETF, "CRYPTOCURRENCY": CRYPTO}


def normalise_symbol(text: str) -> str:
    """``btc`` -> ``BTC-USD``; ``brk.b`` -> ``BRK-B``; anything else upper-cased."""
    symbol = text.strip().upper()
    if symbol in CRYPTO_YAHOO:
        return CRYPTO_YAHOO[symbol]
    if symbol in CRYPTO_ALIASES:
        return f"{symbol}-USD"
    if "." in symbol and not symbol.endswith((".T", ".HK", ".KS", ".KQ", ".TW", ".SS", ".SZ", ".L", ".DE", ".WA")):
        symbol = symbol.replace(".", "-")
    return symbol


def asset_class(symbol: str, fundamentals: dict, known_etfs: set[str]) -> str:
    quote_type = str(fundamentals.get("quote_type") or "").upper()
    if quote_type in _QUOTE_TYPES:
        return _QUOTE_TYPES[quote_type]
    if symbol.endswith("-USD"):
        return CRYPTO
    if symbol in known_etfs:
        return ETF
    return STOCK


def describe(symbol: str, provider, config: dict) -> dict:
    """Everything the quote card shows, or ``{"error": ...}``."""
    lookback = int(config.get("lookback_days", 420))
    prices = provider.get_prices(symbol, lookback)
    if prices is None or prices.empty:
        return {"symbol": symbol, "error": "brak notowań u dostawcy — sprawdź symbol"}

    fundamentals = provider.get_fundamentals(symbol) or {}
    kind = asset_class(symbol, fundamentals, set(config.get("known_etfs") or []))
    bench_symbol = "BTC-USD" if kind == CRYPTO else config.get("benchmark", "SPY")
    benchmark = None
    if bench_symbol and bench_symbol != symbol:
        bench = provider.get_prices(bench_symbol, lookback)
        benchmark = bench["close"] if bench is not None and not bench.empty else None

    card = {
        "symbol": symbol,
        "asset_class": kind,
        "benchmark": bench_symbol if benchmark is not None else None,
        "name": fundamentals.get("name") or symbol,
        "currency": fundamentals.get("currency"),
        "market_cap": fundamentals.get("market_cap"),
        "total_assets": fundamentals.get("total_assets"),
        "category": fundamentals.get("category"),
        "sector": fundamentals.get("sector"),
        "trailing_pe": fundamentals.get("trailing_pe"),
        "forward_pe": fundamentals.get("forward_pe"),
        "revenue_growth": fundamentals.get("revenue_growth"),
        "closes": prices["close"],
    }
    card.update(compute_technical_metrics(prices, benchmark))
    card["trend"] = trend_label(card)
    return card


def trend_label(card: dict) -> str:
    """Plain-language trend from price vs. its 50/200-day averages."""
    above50 = (card.get("px_vs_sma50") or 0) > 0
    above200 = card.get("px_vs_sma200")
    if above200 is None:
        return "za krótka historia"
    if above200 > 0 and above50:
        return "wzrostowy"
    if above200 < 0 and not above50:
        return "spadkowy"
    return "boczny / zmiana trendu"
