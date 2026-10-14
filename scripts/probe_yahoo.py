"""Print what Yahoo Finance actually returns for the data Trela's model needs.

Run on GitHub Actions (task `probe`); the cloud session reads the log to
confirm field names and history depth before trusting the Trela scorer.
"""

from __future__ import annotations

import sys

import pandas as pd
import yfinance as yf

INFO_KEYS = [
    "marketCap", "trailingEps", "epsTrailingTwelveMonths", "ebitdaMargins", "ebitda",
    "totalRevenue", "numberOfAnalystOpinions", "targetMeanPrice", "currentPrice",
    "firstTradeDateEpochUtc", "firstTradeDateMilliseconds", "exchange", "quoteType",
    "financialCurrency", "currency",
]


def show(title: str, frame) -> None:
    print(f"\n--- {title} ---")
    if frame is None:
        print("None")
        return
    if isinstance(frame, dict):
        print(frame)
        return
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(f"shape={getattr(frame, 'shape', None)}")
        print(frame)


def probe(symbol: str) -> None:
    print(f"\n================ {symbol} ================")
    t = yf.Ticker(symbol)
    info = t.info or {}
    print({k: info.get(k) for k in INFO_KEYS})
    for name in ("earnings_estimate", "revenue_estimate", "growth_estimates", "eps_trend"):
        try:
            show(name, getattr(t, name))
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: ERROR {exc}")
    try:
        ud = t.upgrades_downgrades
        print(f"\n--- upgrades_downgrades --- rows={0 if ud is None else len(ud)}")
        if ud is not None and len(ud):
            print("columns:", list(ud.columns))
            print("oldest:", ud.index.min(), "newest:", ud.index.max())
            print(ud.head(8))
    except Exception as exc:  # noqa: BLE001
        print(f"upgrades_downgrades: ERROR {exc}")
    for name, rows in (
        ("income_stmt", ["Total Revenue", "Basic EPS", "EBIT", "EBITDA"]),
        ("cashflow", ["Operating Cash Flow"]),
        ("balance_sheet", ["Total Assets", "Working Capital", "Retained Earnings",
                           "Total Liabilities Net Minority Interest", "Stockholders Equity"]),
    ):
        try:
            frame = getattr(t, name)
            present = [r for r in rows if r in frame.index]
            print(f"\n--- {name} --- columns={list(frame.columns.date) if len(frame.columns) else []}")
            print("missing rows:", [r for r in rows if r not in frame.index])
            if present:
                print(frame.loc[present])
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: ERROR {exc}")
    try:
        hist = t.history(period="max", auto_adjust=True)
        print(f"\nhistory: {len(hist)} bars from {hist.index.min()} to {hist.index.max()}")
    except Exception as exc:  # noqa: BLE001
        print(f"history: ERROR {exc}")


if __name__ == "__main__":
    for symbol in sys.argv[1:] or ["NVDA", "TSM", "6324.T", "005930.KS"]:
        probe(symbol)
