"""Command-line interface: python -m tracker <komenda>."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from screener.cache import Cache
from screener.config import load_config
from screener.providers import ProviderError, available_providers, get_provider

from . import report
from .funds import load_funds
from .instruments import CRYPTO, CRYPTO_ALIASES, describe, normalise_symbol
from .lists import load_symbols, tickers
from .models import BUY, SELL
from .signals import build_signals
from .sources import FeedError, available_feeds, get_feed
from .state import SeenStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Tracker transakcji Wall Street: Kongres USA, insiderzy (Form 4), fundusze (13F) "
                    "oraz wyszukiwarka akcji, ETF i krypto.",
    )
    parser.add_argument("--config", default="config/tracker.yml", help="plik konfiguracji")
    parser.add_argument("--feed", choices=available_feeds(), help="źródło transakcji (nadpisuje config)")
    parser.add_argument("--provider", choices=available_providers(), help="źródło notowań (nadpisuje config)")
    parser.add_argument("--no-cache", action="store_true", help="pobierz wszystko od nowa")

    sub = parser.add_subparsers(dest="command", required=True)

    find = sub.add_parser("find", help="znajdź ticker po nazwie lub fragmencie symbolu")
    find.add_argument("text", nargs="+", help="np. nvidia, berkshire, btc")

    quote = sub.add_parser("quote", help="karta instrumentu: akcja, ETF lub krypto + kto nim handlował")
    quote.add_argument("symbols", nargs="+", help="np. NVDA SPY BTC")
    quote.add_argument("--no-activity", action="store_true", help="bez transakcji Kongresu/insiderów")

    congress = sub.add_parser("congress", help="transakcje członków Kongresu USA")
    congress.add_argument("--days", type=int, help="okno w dniach (domyślnie z configu)")
    congress.add_argument("--ticker", help="tylko ten ticker")
    congress.add_argument("--member", help="fragment nazwiska, np. pelosi")
    congress.add_argument("--side", choices=[BUY, SELL], help="tylko kupno albo sprzedaż")

    insiders = sub.add_parser("insiders", help="transakcje insiderów (SEC Form 4)")
    insiders.add_argument("tickers", nargs="*", help="spółki; domyślnie portfel + obserwowane")
    insiders.add_argument("--days", type=int, help="okno w dniach")
    insiders.add_argument("--buys-only", action="store_true", help="tylko zakupy na rynku")

    funds = sub.add_parser("funds", help="zmiany w portfelach funduszy (13F)")
    funds.add_argument("keys", nargs="*", help="np. berkshire ark; domyślnie wszystkie z listy")
    funds.add_argument("--top", type=int, default=15, help="ile zmian pokazać na fundusz")
    funds.add_argument("--all", action="store_true", help="pokaż też pozycje bez zmian")

    scan = sub.add_parser("scan", help="pełny skan: sygnały pod portfel + raport HTML (do rutyny co godzinę)")
    scan.add_argument("--new-only", action="store_true", help="w konsoli tylko to, co nowe od ostatniego skanu")
    scan.add_argument("--no-quotes", action="store_true", help="pomiń notowania portfela/obserwowanych")
    scan.add_argument("--no-funds", action="store_true", help="pomiń 13F")
    scan.add_argument("--no-html", action="store_true", help="nie zapisuj raportu HTML")
    scan.add_argument("--out-dir", default="out", help="katalog na raporty")
    scan.add_argument("--top", type=int, default=25, help="ile sygnałów pokazać w konsoli")

    alerts = sub.add_parser("alerts", help="anomalie: skoki wolumenu i ceny, wybicia, okazje zakupowe (do rutyny co godzinę)")
    alerts.add_argument("--universe", action="append", default=[], metavar="PLIK.csv",
                        help="listy spółek do sprawdzenia; domyślnie wszystkie z configu (alerts_universes)")
    alerts.add_argument("--all", action="store_true", help="pokaż wszystkie alerty, nie tylko nowe od ostatniego razu")
    alerts.add_argument("--no-smart", action="store_true", help="pomiń transakcje insiderów/Kongresu")
    alerts.add_argument("--discord", action="store_true", help="wyślij na Discord (DISCORD_WEBHOOK_URL)")
    alerts.add_argument("--out-dir", default="out", help="katalog na JSON z alertami")

    sub.add_parser("check", help="sprawdź konfigurację i dostęp do źródeł danych")
    return parser


class Context:
    def __init__(self, args, config):
        self.args = args
        self.config = config
        root = config.get("cache_dir", ".cache")
        self.fresh_cache = Cache(root, ttl_hours=config.get("fresh_cache_hours", 0.5),
                                 enabled=not args.no_cache)
        self.archive_cache = Cache(root, ttl_hours=24 * 365, enabled=not args.no_cache)
        self.price_cache = Cache(root, ttl_hours=config.get("price_cache_hours", 4),
                                 enabled=not args.no_cache)
        self.feed = get_feed(args.feed or config.get("feed", "live"), config,
                             fresh_cache=self.fresh_cache, archive_cache=self.archive_cache)
        self._provider = None

    @property
    def provider(self):
        if self._provider is None:
            name = self.args.provider or self.config.get("price_provider", "yahoo")
            if (self.args.feed or self.config.get("feed")) == "fixture" and not self.args.provider:
                name = "fixture"
            self._provider = get_provider(name, cache=self.price_cache)
        return self._provider

    def since(self, key: str, override: int | None = None) -> date:
        return date.today() - timedelta(days=int(override or self.config.get(key, 30)))

    def portfolio(self) -> list[dict]:
        rows = load_symbols(self.config.get("portfolio", "data/portfolio.csv"))
        if not rows:
            example = self.config.get("portfolio_example")
            if example and Path(example).exists():
                self.feed.warn(f"Brak {self.config.get('portfolio')} — używam przykładu {example}. "
                               "Skopiuj go i wpisz swoje pozycje.")
                rows = load_symbols(example)
        return rows

    def watchlist(self) -> list[dict]:
        return load_symbols(self.config.get("watchlist", "data/watchlist.csv"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Błąd konfiguracji: {exc}", file=sys.stderr)
        return 2

    try:
        ctx = Context(args, config)
    except (FeedError, ProviderError) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 2

    handlers = {"find": _cmd_find, "quote": _cmd_quote, "congress": _cmd_congress,
                "insiders": _cmd_insiders, "funds": _cmd_funds, "scan": _cmd_scan, "check": _cmd_check,
                "alerts": _cmd_alerts}
    try:
        code = handlers[args.command](ctx)
    except (FeedError, ProviderError, FileNotFoundError, ValueError) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    if args.command != "scan":
        _print_warnings(ctx.feed.warnings)
    return code


def _print_warnings(warnings: list[str]) -> None:
    if warnings:
        print("\nOstrzeżenia:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)


# -- commands ----------------------------------------------------------------


def _cmd_find(ctx: Context) -> int:
    text = " ".join(ctx.args.text)
    hits = [(f"{c}-USD", f"krypto ({c})") for c in sorted(CRYPTO_ALIASES) if c.startswith(text.strip().upper())]
    try:
        hits += ctx.feed.search_names(text)
    except Exception as exc:
        ctx.feed.warn(f"Wyszukiwanie po nazwie niedostępne ({exc}).")
    if not hits:
        print(f"Nic nie znaleziono dla „{text}”.")
        return 1
    print(report.table(["Ticker", "Nazwa"], [[t, n] for t, n in hits]))
    print("\nSzczegóły: python -m tracker quote TICKER")
    return 0


def _cmd_quote(ctx: Context) -> int:
    congress = [] if ctx.args.no_activity else ctx.feed.congress_trades(ctx.since("congress_days"))
    failures = 0
    for raw in ctx.args.symbols:
        symbol = normalise_symbol(raw)
        card = describe(symbol, ctx.provider, ctx.config)
        print(report.render_quote(card))
        if card.get("error"):
            failures += 1
            continue
        if ctx.args.no_activity or card["asset_class"] == CRYPTO:
            continue
        mine = [t for t in congress if t.ticker == symbol]
        insiders = ctx.feed.insider_trades(symbol, ctx.since("insider_days"))
        if mine:
            print(report.render_trades("  Kongres", mine))
        if insiders:
            print(report.render_trades("  Insiderzy", insiders))
        if not mine and not insiders:
            print("  Brak transakcji Kongresu i insiderów w oknie czasowym.")
    return 1 if failures == len(ctx.args.symbols) else 0


def _cmd_congress(ctx: Context) -> int:
    a = ctx.args
    trades = ctx.feed.congress_trades(ctx.since("congress_days", a.days))
    if a.ticker:
        trades = [t for t in trades if t.ticker == normalise_symbol(a.ticker)]
    if a.member:
        trades = [t for t in trades if a.member.lower() in t.actor.lower()]
    if a.side:
        trades = [t for t in trades if t.side == a.side]
    print(report.render_trades("KONGRES USA", trades))
    signals = build_signals(trades, [], weights=ctx.config.get("signal_weights"))
    if signals:
        print(report.render_signals(signals, top=15))
    return 0


def _cmd_insiders(ctx: Context) -> int:
    a = ctx.args
    names = [normalise_symbol(t) for t in a.tickers] or sorted(
        t for t in tickers(ctx.portfolio()) | tickers(ctx.watchlist()) if not t.endswith("-USD")
    )
    since = ctx.since("insider_days", a.days)
    trades = []
    for i, ticker in enumerate(names, 1):
        print(f"  [{i}/{len(names)}] {ticker}", end="\r", file=sys.stderr, flush=True)
        trades.extend(ctx.feed.insider_trades(ticker, since))
    print(" " * 40, end="\r", file=sys.stderr)
    if a.buys_only:
        trades = [t for t in trades if t.side == BUY]
    print(report.render_trades("INSIDERZY (Form 4)", trades))
    return 0


def _cmd_funds(ctx: Context) -> int:
    funds = load_funds(ctx.config.get("funds", "data/funds_13f.csv"))
    if ctx.args.keys:
        wanted = {k.lower() for k in ctx.args.keys}
        funds = [f for f in funds if f.key.lower() in wanted]
        if not funds:
            print("Nie znam takiego funduszu. Dostępne klucze są w data/funds_13f.csv.", file=sys.stderr)
            return 1
    for fund in funds:
        rep = ctx.feed.fund_report(fund)
        if rep is not None:
            print(report.render_fund(rep, top=ctx.args.top, show_hold=ctx.args.all))
    return 0


def _cmd_scan(ctx: Context) -> int:
    a, cfg = ctx.args, ctx.config
    portfolio, watchlist = tickers(ctx.portfolio()), tickers(ctx.watchlist())
    store = SeenStore(cfg.get("state_file", ".cache/tracker_seen.json"))

    congress = ctx.feed.congress_trades(ctx.since("congress_days"))

    # Insider lookups cost requests, so check what matters: holdings and
    # watchlist first, then names Congress has been buying.
    focus = sorted(t for t in portfolio | watchlist if not t.endswith("-USD"))
    bought = [t.ticker for t in congress if t.side == BUY and t.ticker not in focus]
    candidates = list(dict.fromkeys(focus + bought))[: int(cfg.get("insider_max_tickers", 40))]
    insiders = []
    for i, ticker in enumerate(candidates, 1):
        print(f"  insiderzy [{i}/{len(candidates)}] {ticker}   ", end="\r", file=sys.stderr, flush=True)
        insiders.extend(ctx.feed.insider_trades(ticker, ctx.since("insider_days")))
    print(" " * 50, end="\r", file=sys.stderr)

    fund_reports = []
    if not a.no_funds:
        for fund in load_funds(cfg.get("funds", "data/funds_13f.csv")):
            rep = ctx.feed.fund_report(fund)
            if rep is not None:
                fund_reports.append(rep)

    trades = congress + insiders
    new_trades = store.new(trades)
    new_keys = {t.key for t in new_trades}
    new_funds = [r for r in fund_reports if store.is_new_key(f"13f|{r.fund.key}|{r.filed_now}")]

    signals = build_signals(trades, fund_reports, portfolio, watchlist, cfg.get("signal_weights"))

    quotes = []
    if not a.no_quotes:
        for symbol in sorted(portfolio | watchlist, key=lambda s: (s not in portfolio, s)):
            try:
                quotes.append(describe(symbol, ctx.provider, cfg))
            except Exception as exc:
                quotes.append({"symbol": symbol, "error": str(exc)})

    result = report.ScanResult(
        run_date=date.today().isoformat(), feed_name=ctx.feed.name,
        congress=congress, insiders=insiders, funds=fund_reports, signals=signals,
        quotes=quotes, new_keys=new_keys, warnings=ctx.feed.warnings,
        congress_days=int(cfg.get("congress_days", 30)), insider_days=int(cfg.get("insider_days", 30)),
    )

    # -- console
    if a.new_only:
        touched = {t.ticker for t in new_trades} | {
            c.ticker for r in new_funds for c in r.changes if c.ticker and c.kind != "hold"}
        if not new_trades and not new_funds:
            print(f"Brak nowych transakcji od ostatniego skanu ({len(trades)} w oknie czasowym).")
        else:
            print(f"NOWE od ostatniego skanu: {len(new_trades)} transakcji, {len(new_funds)} zgłoszeń 13F.")
            print(report.render_trades("Nowe transakcje", new_trades, new_keys))
            for rep in new_funds:
                print(report.render_fund(rep, top=10))
            print(report.render_signals([s for s in signals if s.ticker in touched], top=a.top))
    else:
        print(report.render_trades("KONGRES USA", congress, new_keys))
        print(report.render_trades("INSIDERZY", insiders, new_keys))
        for rep in fund_reports:
            print(report.render_fund(rep, top=10))
        print(report.render_signals(signals, top=a.top))

    alerts = [s for s in signals if s.alert]
    if alerts:
        print("\nALERT PORTFELA: przewaga sprzedających w " + ", ".join(s.ticker for s in alerts))

    # -- files
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    json_path = out_dir / f"signals_{stamp}.json"
    json_path.write_text(json.dumps(_signals_json(result, new_trades), ensure_ascii=False, indent=2,
                                    default=str), encoding="utf-8")
    print(f"\nJSON: {json_path}", file=sys.stderr)
    if not a.no_html:
        print(f"HTML: {report.render_html(result, out_dir / f'tracker_{stamp}.html')}", file=sys.stderr)

    _print_warnings(ctx.feed.warnings)

    store.remember(trades)
    for rep in fund_reports:
        store.remember_key(f"13f|{rep.fund.key}|{rep.filed_now}")
    store.save()
    return 0


def _cmd_alerts(ctx: Context) -> int:
    from .alerts import DEFAULTS, AlertRun, detect, order, smart_money_alerts
    from .notify import format_text, send_discord

    a, cfg = ctx.args, ctx.config
    rules = {**DEFAULTS, **(cfg.get("alert_rules") or {})}
    portfolio = tickers(ctx.portfolio())
    dips = {r["ticker"]: float(r.get("max_drawdown_pct") or rules["dip_default_pct"])
            for r in load_symbols(cfg.get("dip_list", "data/okazje.csv"))}

    files = a.universe or cfg.get("alerts_universes") or []
    symbols: dict[str, str] = {}
    for path in files:
        for row in load_symbols(path):
            symbols.setdefault(row["ticker"], row.get("name") or row["ticker"])
    for t in portfolio | set(dips) | tickers(ctx.watchlist()):
        symbols.setdefault(t, t)

    lookback = int(cfg.get("lookback_days", 420))
    run = AlertRun(run_date=date.today().isoformat())
    for i, (ticker, name) in enumerate(sorted(symbols.items()), 1):
        print(f"  [{i}/{len(symbols)}] {ticker}   ", end="\r", file=sys.stderr, flush=True)
        try:
            prices = ctx.provider.get_prices(ticker, lookback)
        except Exception as exc:
            run.warnings.append(f"{ticker}: {exc}")
            continue
        if prices is None or prices.empty:
            run.warnings.append(f"{ticker}: brak notowań")
            continue
        run.checked += 1
        run.alerts.extend(detect(ticker, name, prices, rules, dips.get(ticker), ticker in portfolio))
    print(" " * 40, end="\r", file=sys.stderr)

    store = SeenStore(cfg.get("alerts_state_file", ".cache/tracker_alerts_seen.json"))
    if not a.no_smart:
        since = ctx.since("insider_days", 7)
        trades = ctx.feed.congress_trades(since)
        for t in sorted(portfolio | set(dips)):
            if not t.endswith("-USD"):
                trades.extend(ctx.feed.insider_trades(t, since))
        trade_store = SeenStore(cfg.get("state_file", ".cache/tracker_seen.json"))
        fresh = trade_store.new(trades)
        run.alerts.extend(smart_money_alerts(fresh, portfolio))
        run.warnings.extend(ctx.feed.warnings)

    fresh_alerts = [x for x in run.alerts if store.is_new_key(x.key)]
    shown = order(run.alerts if a.all else fresh_alerts)
    title = f"Alerty {run.run_date} — {len(shown)} {'łącznie' if a.all else 'nowych'} ({run.checked} instrumentów)"
    print(format_text(shown, title, markdown=False))

    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"alerts_{run.run_date}.json").write_text(json.dumps({
        "run_date": run.run_date, "checked": run.checked,
        "alerts": [x.__dict__ for x in shown], "warnings": run.warnings,
    }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if a.discord and shown:
        try:
            sent = send_discord(format_text(shown, title))
            print("Discord: wysłano" if sent else "Discord: brak DISCORD_WEBHOOK_URL — nie wysłano", file=sys.stderr)
        except Exception as exc:
            print(f"Discord: błąd wysyłki ({exc})", file=sys.stderr)
    elif a.discord:
        print("Discord: nic nowego, nie wysyłam", file=sys.stderr)

    for x in run.alerts:
        store.remember_key(x.key)
    store.save()
    _print_warnings(run.warnings)
    return 0


def _signals_json(result: report.ScanResult, new_trades) -> dict:
    """Machine-readable output, e.g. for a Claude routine to summarise."""
    return {
        "run_date": result.run_date,
        "feed": result.feed_name,
        "new_trades": [{
            "source": t.source, "ticker": t.ticker, "side": t.side, "actor": t.actor, "role": t.role,
            "amount_low": t.amount_low, "amount_high": t.amount_high,
            "traded": t.traded, "reported": t.reported, "planned_10b5_1": t.planned,
        } for t in new_trades],
        "signals": [{
            "ticker": s.ticker, "score": round(s.score, 2), "label": s.label,
            "in_portfolio": s.in_portfolio, "on_watchlist": s.on_watchlist, "alert": s.alert,
            "buyers": sorted(s.buyers), "sellers": sorted(s.sellers), "reasons": s.reasons,
        } for s in result.signals],
        "warnings": result.warnings,
    }


def _cmd_check(ctx: Context) -> int:
    print("Konfiguracja trackera\n")
    ua = os.environ.get("SEC_USER_AGENT") or ctx.config.get("sec_user_agent")
    print(f"  SEC_USER_AGENT     {'ustawiony' if ua else 'BRAK — wymagany dla feed: live'}")
    print(f"  QUIVER_API_KEY     {'ustawiony' if os.environ.get('QUIVER_API_KEY') else 'brak — Kongres wyłączony'}")
    print(f"  źródło transakcji  {ctx.feed.name}")
    print(f"  portfel            {len(ctx.portfolio())} pozycji")
    print(f"  obserwowane        {len(ctx.watchlist())} symboli")
    funds = load_funds(ctx.config.get("funds", "data/funds_13f.csv"))
    print(f"  fundusze 13F       {', '.join(f.key for f in funds)}")

    print("\nTest źródeł:")
    ok = True
    try:
        hits = ctx.feed.search_names("NVDA", limit=1)
        print(f"  SEC lista spółek   OK ({hits[0][1] if hits else 'brak NVDA?'})")
    except Exception as exc:
        ok = False
        print(f"  SEC lista spółek   BŁĄD: {exc}")
    trades = ctx.feed.insider_trades("NVDA", ctx.since("insider_days", 120))
    print(f"  SEC Form 4 (NVDA)  {len(trades)} transakcji w 120 dni")
    congress = ctx.feed.congress_trades(ctx.since("congress_days"))
    print(f"  Kongres            {len(congress)} transakcji")
    card = describe("SPY", ctx.provider, ctx.config)
    print(f"  Notowania (SPY)    {'BŁĄD: ' + card['error'] if card.get('error') else 'OK'}")
    ok = ok and not card.get("error")
    return 0 if ok else 1
