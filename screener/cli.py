"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from .analysis.fundamental import compute_fundamental_metrics
from .analysis.scoring import LABELS
from .analysis.technical import compute_technical_metrics
from .cache import Cache
from .config import benchmark_for, load_config
from .pipeline import run_screen
from .providers import ProviderError, available_providers, get_provider
from .report import format as fmt
from .report.console import render_console
from .report.html import render_html
from .universe import load_universe

# Columns written to CSV, in this order. Everything else stays in the frame
# for the HTML report but would only clutter a spreadsheet.
CSV_COLUMNS = [
    "ticker", "name", "market", "segment",
    "composite_score", "fundamental_score", "technical_score",
    "fundamental_coverage", "technical_coverage",
    "market_cap_usd", "currency",
    "revenue_growth", "earnings_growth", "gross_margin", "operating_margin",
    "profit_margin", "return_on_equity", "return_on_assets", "fcf_margin",
    "debt_to_equity", "current_ratio", "net_cash_to_mcap",
    "trailing_pe", "forward_pe", "price_to_sales", "price_to_book", "ev_to_ebitda",
    "last_close", "px_vs_sma50", "px_vs_sma200", "sma50_vs_sma200",
    "rsi14", "macd_hist_pct",
    "ret_1m", "ret_3m", "ret_6m", "ret_12m", "rs_3m", "rs_6m",
    "dist_52w_high", "pos_52w_range", "max_drawdown_12m", "atr_pct",
    "avg_turnover_usd", "benchmark", "notes",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="screener",
        description="Screener spółek z sektora robotyki humanoidalnej na rynkach azjatyckich "
                    "— analiza fundamentalna i techniczna.",
    )
    parser.add_argument("--config", default="config/default.yml", help="ścieżka do pliku konfiguracji")
    parser.add_argument("--provider", choices=available_providers(), help="źródło danych (nadpisuje config)")
    parser.add_argument("--universe", help="plik CSV z uniwersum (nadpisuje config)")
    parser.add_argument("--no-cache", action="store_true", help="pomiń cache i pobierz dane od nowa")

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="przeprowadź pełny screening i zapisz raport")
    run.add_argument("--profile", help="profil scoringu: growth / value / balanced")
    run.add_argument("--top", type=int, help="pokaż w konsoli tylko N najlepszych spółek")
    run.add_argument("--limit", type=int, help="ogranicz uniwersum do N pierwszych spółek (do testów)")
    run.add_argument("--out-dir", default="out", help="katalog na raporty (domyślnie: out)")
    run.add_argument("--no-html", action="store_true", help="nie generuj raportu HTML")

    validate = sub.add_parser(
        "validate",
        help="sprawdź, czy każdy ticker z uniwersum rozwiązuje się u dostawcy danych",
    )
    validate.add_argument("--limit", type=int, help="sprawdź tylko N pierwszych spółek")

    site = sub.add_parser("site", help="wygeneruj stronę WWW z listą spółek (do wgrania na serwer)")
    site.add_argument("--profile", help="profil scoringu")
    site.add_argument("--limit", type=int, help="ogranicz uniwersum do N pierwszych spółek (do testów)")
    site.add_argument("--out", default="out/site/roboty.html", help="docelowy plik HTML")
    site.add_argument("--signals", help="plik signals_*.json z trackera - dołoży kolumnę Insiderzy")
    site.add_argument("--title", default="Robotyka humanoidalna — spółki i dostawcy podzespołów")

    show = sub.add_parser("show", help="wypisz komplet wskaźników dla jednej spółki")
    show.add_argument("ticker", help="np. 6324.T")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Błąd konfiguracji: {exc}", file=sys.stderr)
        return 2

    provider_name = args.provider or config.get("provider", "yahoo")
    cache = Cache(
        root=config.get("cache_dir", ".cache"),
        ttl_hours=config.get("cache_ttl_hours", 12),
        enabled=not args.no_cache,
    )

    try:
        provider = get_provider(provider_name, cache=cache)
    except ProviderError as exc:
        print(f"Błąd dostawcy danych: {exc}", file=sys.stderr)
        return 2

    handlers = {"run": _cmd_run, "validate": _cmd_validate, "show": _cmd_show, "site": _cmd_site}
    try:
        return handlers[args.command](args, config, provider)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1


def _universe_for(args, config) -> pd.DataFrame:
    path = args.universe or config.get("universe", "data/universe_humanoid_asia.csv")
    universe = load_universe(path)
    limit = getattr(args, "limit", None)
    return universe.head(limit) if limit else universe


def _cmd_run(args, config, provider) -> int:
    universe = _universe_for(args, config)
    print(f"Screening {len(universe)} spółek (źródło: {provider.name})...", file=sys.stderr)

    def progress(position: int, total: int, ticker: str) -> None:
        print(f"  [{position}/{total}] {ticker}", end="\r", file=sys.stderr, flush=True)

    result = run_screen(universe, provider, config, args.profile, progress=progress)
    print(" " * 60, end="\r", file=sys.stderr)

    print(render_console(result, top=args.top))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()

    csv_path = out_dir / f"screen_{stamp}.csv"
    _write_csv(result.ranked, csv_path)
    print(f"\nCSV:  {csv_path}", file=sys.stderr)

    if not args.no_html:
        html_path = render_html(result, out_dir / f"report_{stamp}.html")
        print(f"HTML: {html_path}", file=sys.stderr)

    return 0


def _cmd_site(args, config, provider) -> int:
    import json

    from .report.site import render_site

    universe = _universe_for(args, config)
    print(f"Strona dla {len(universe)} spółek (źródło: {provider.name})...", file=sys.stderr)

    def progress(position: int, total: int, ticker: str) -> None:
        print(f"  [{position}/{total}] {ticker}", end="\r", file=sys.stderr, flush=True)

    result = run_screen(universe, provider, config, args.profile, progress=progress)
    print(" " * 60, end="\r", file=sys.stderr)

    signals = None
    if args.signals:
        signals = json.loads(Path(args.signals).read_text(encoding="utf-8"))

    path = render_site(result, args.out, signals=signals, title=args.title)
    print(f"Strona: {path}", file=sys.stderr)
    for warning in result.warnings:
        print(f"  ! {warning}", file=sys.stderr)
    return 0


def _write_csv(ranked: pd.DataFrame, path: Path) -> None:
    columns = [c for c in CSV_COLUMNS if c in ranked.columns]
    ranked.to_csv(path, columns=columns, index=False, float_format="%.6g")


def _cmd_validate(args, config, provider) -> int:
    """Confirm every ticker resolves before trusting a screen built on it."""
    universe = _universe_for(args, config)
    lookback = int(config.get("lookback_days", 420))
    print(f"Weryfikacja {len(universe)} tickerów u dostawcy '{provider.name}'...\n")

    header = f"{'Ticker':<11}{'Sesje':>7}  {'Fund.':>6}  {'Nazwa z pliku':<30}Status"
    print(header)
    print("-" * len(header))

    failures = 0
    for entry in universe.to_dict("records"):
        ticker = entry["ticker"]
        prices = provider.get_prices(ticker, lookback)
        bars = 0 if prices is None or prices.empty else len(prices)
        fundamentals = provider.get_fundamentals(ticker) or {}

        if bars == 0:
            status, failures = "BŁĄD — brak notowań", failures + 1
        elif bars < 200:
            status = "OSTRZEŻENIE — krótka historia"
        elif not fundamentals:
            status = "OSTRZEŻENIE — brak fundamentów"
        else:
            status = "OK"

        print(
            f"{ticker:<11}{bars:>7}  {len(fundamentals):>6}  "
            f"{(entry.get('name') or '')[:29]:<30}{status}"
        )

    print()
    if failures:
        print(f"{failures} tickerów nie rozwiązało się — popraw je w pliku uniwersum.")
        return 1
    print("Wszystkie tickery rozwiązały się poprawnie.")
    return 0


def _cmd_show(args, config, provider) -> int:
    ticker = args.ticker
    lookback = int(config.get("lookback_days", 420))

    prices = provider.get_prices(ticker, lookback)
    if prices is None or prices.empty:
        print(f"Brak danych cenowych dla {ticker}.", file=sys.stderr)
        return 1

    benchmark_symbol = benchmark_for(ticker, config)
    benchmark = provider.get_prices(benchmark_symbol, lookback) if benchmark_symbol else None
    benchmark_close = benchmark["close"] if benchmark is not None and not benchmark.empty else None

    technical = compute_technical_metrics(prices, benchmark_close)
    fundamental = compute_fundamental_metrics(provider.get_fundamentals(ticker))

    print(f"\n{fundamental.get('name') or ticker}  ({ticker})")
    print(f"{fundamental.get('sector') or '?'} · {fundamental.get('industry') or '?'} · "
          f"waluta {fundamental.get('currency') or '?'} · benchmark {benchmark_symbol or '—'}")
    print(f"Sesje w oknie: {technical.get('bars', 0)}  |  Ostatni kurs: {fmt.num(technical.get('last_close'), 2)}")

    _print_block("FUNDAMENTY", fundamental, _FUNDAMENTAL_VIEW)
    _print_block("TECHNIKA", technical, _TECHNICAL_VIEW)
    print()
    return 0


# (key, formatter) pairs; formatter names map onto screener.report.format.
_FUNDAMENTAL_VIEW = [
    ("market_cap", "raw"), ("revenue_growth", "pct"), ("earnings_growth", "pct"),
    ("gross_margin", "pct"), ("operating_margin", "pct"), ("profit_margin", "pct"),
    ("return_on_equity", "pct"), ("return_on_assets", "pct"), ("fcf_margin", "pct"),
    ("debt_to_equity", "num"), ("current_ratio", "num"), ("net_cash_to_mcap", "pct"),
    ("trailing_pe", "num"), ("forward_pe", "num"), ("price_to_sales", "num"),
    ("price_to_book", "num"), ("ev_to_ebitda", "num"),
]

_TECHNICAL_VIEW = [
    ("px_vs_sma50", "pct"), ("px_vs_sma200", "pct"), ("sma50_vs_sma200", "pct"),
    ("rsi14", "num"), ("macd_hist_pct", "pct"),
    ("ret_1m", "pct"), ("ret_3m", "pct"), ("ret_6m", "pct"), ("ret_12m", "pct"),
    ("rs_3m", "pct"), ("rs_6m", "pct"),
    ("dist_52w_high", "pct"), ("pos_52w_range", "pct"),
    ("max_drawdown_12m", "pct"), ("atr_pct", "pct"),
]


def _print_block(title: str, values: dict, view: list[tuple[str, str]]) -> None:
    print(f"\n{title}")
    print("-" * 46)
    for key, kind in view:
        value = values.get(key)
        if kind == "pct":
            text = fmt.pct(value, signed=key.startswith(("ret_", "rs_", "px_vs", "sma50_vs", "macd")))
        elif kind == "num":
            text = fmt.num(value, 2)
        else:
            text = f"{value:,.0f}".replace(",", " ") if isinstance(value, (int, float)) else fmt.DASH
        print(f"  {LABELS.get(key, key):<28}{text:>16}")
