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
from screener.report import format as fmt
from .env import load_dotenv
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

    market = sub.add_parser("market", help="skan całego rynku USA: spółki, które właśnie zaczynają ruch (EMA30 + wolumen)")
    market.add_argument("--rule", action="append", default=[], help="reguła (domyślnie wszystkie): ema30")
    market.add_argument("--symbols", help="własny plik CSV z symbolami zamiast pełnej listy SEC")
    market.add_argument("--source", choices=["sec", "tradingview"], default=None,
                        help="skąd brać kandydatów: sec (pełny spis USA) albo tradingview (screener TV, też Europa/Azja); domyślnie z configu")
    market.add_argument("--tv-market", default=None, help="rynek screenera TV: america, global, germany, japan, poland")
    market.add_argument("--limit", type=int, help="sprawdź tylko N pierwszych symboli (do testów)")
    market.add_argument("--all", action="store_true", help="pokaż wszystkie, nie tylko nowe od ostatniego skanu")
    market.add_argument("--top", type=int, default=30, help="ile najmocniejszych pokazać")
    market.add_argument("--discord", action="store_true", help="wyślij na Discord")
    market.add_argument("--out-dir", default="out")

    replay = sub.add_parser("replay", help="odtwórz regułę skanu na historii jednego symbolu: w które dni by odpaliła")
    replay.add_argument("symbol", help="np. ARB-USD, NVDA")
    replay.add_argument("--rule", default="pullback", help="pullback | ema30")
    replay.add_argument("--days", type=int, default=120, help="ile ostatnich sesji przejrzeć")

    dump = sub.add_parser("dump", help="wypisz notowania (CSV) wybranych symboli — do zapisania jako data/samples/*.csv")
    dump.add_argument("symbols", nargs="+", help="np. ARB-USD NVDA BTC")
    dump.add_argument("--days", type=int, default=400)

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
    load_dotenv()
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
                "alerts": _cmd_alerts, "market": _cmd_market, "replay": _cmd_replay, "dump": _cmd_dump}
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
    from .alerts import DEFAULTS, AlertRun, detect, mark_confluence, order, smart_money_alerts
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

    run.alerts = mark_confluence(run.alerts, int(rules["confluence_min"]))
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


def _market_symbols(ctx: Context) -> list[tuple[str, str]]:
    """(ticker, name) for the whole scan: a CSV if given, else the feed's full list (SEC)."""
    if ctx.args.symbols:
        return [(r["ticker"], r.get("name") or r["ticker"]) for r in load_symbols(ctx.args.symbols)]
    # SEC's list includes warrants, units, preferreds ("-WT", "-U", "-P") — skip them.
    out = []
    for ticker, title in ctx.feed.all_names():
        if any(x in ticker for x in ("-WT", "-U", "-P", "-R", "-UN", "^")) or len(ticker) > 5:
            continue
        out.append((ticker, title))
    return sorted(out)


def _cmd_market(ctx: Context) -> int:
    from .market import DEFAULTS, RULES, MarketScan, liquid_enough
    from .notify import send_discord

    a, cfg = ctx.args, ctx.config
    rules = {**DEFAULTS, **(cfg.get("market_rules") or {})}
    chosen = {k: RULES[k] for k in (a.rule or RULES) if k in RULES}
    source = a.source or cfg.get("market_source", "sec")
    symbols: list[tuple[str, str]] = []
    if source == "tradingview" and not a.symbols:
        from .sources.tradingview import fetch_candidates

        tv_market = a.tv_market or cfg.get("market_tv_market", "america")
        markets = [tv_market] + (["crypto"] if cfg.get("market_crypto") and tv_market != "crypto" else [])
        tv_failed = False
        for m in markets:
            try:
                got = fetch_candidates(m, rules["volume_multiple"], rules["ema_len"],
                                       rules["min_price"], rules["min_avg_dollar_volume"])
                print(f"TradingView screener ({m}): {len(got)} kandydatów do potwierdzenia", file=sys.stderr)
                symbols.extend(got)
                if m == "crypto" and not got:
                    # An empty crypto answer is more likely our query than a quiet market.
                    symbols.extend((r["ticker"], r.get("name") or r["ticker"])
                                   for r in load_symbols(cfg.get("crypto_list", "data/crypto.csv")))
            except Exception as exc:
                # A transport/format failure means "use the fallback"; an empty
                # answer means "nothing matches today" and must NOT trigger the
                # hour-long SEC download.
                if m == "crypto":
                    print(f"TradingView screener (crypto) niedostępny ({exc}) — krypto z listy zapasowej.", file=sys.stderr)
                    symbols.extend((r["ticker"], r.get("name") or r["ticker"])
                                   for r in load_symbols(cfg.get("crypto_list", "data/crypto.csv")))
                else:
                    tv_failed = True
                    print(f"TradingView screener ({m}) niedostępny ({exc}) — wracam do spisu SEC.", file=sys.stderr)
        if tv_failed:
            symbols.extend(_market_symbols(ctx))
    elif source != "tradingview" or a.symbols:
        symbols = _market_symbols(ctx)
    if a.limit:
        symbols = symbols[: a.limit]
    if not symbols:
        print("Brak listy symboli: podaj --symbols PLIK.csv albo użyj feed: live (lista SEC).", file=sys.stderr)
        return 1

    lookback = int(cfg.get("market_lookback_days", 200))
    scan = MarketScan(run_date=date.today().isoformat())
    for i, (ticker, name) in enumerate(symbols, 1):
        if i % 25 == 0 or i == len(symbols):
            print(f"  [{i}/{len(symbols)}] {ticker}   ", end="\r", file=sys.stderr, flush=True)
        try:
            prices = ctx.provider.get_prices(ticker, lookback)
        except Exception as exc:
            scan.warnings.append(f"{ticker}: {exc}")
            continue
        if prices is None or prices.empty:
            continue
        if not liquid_enough(prices, rules):
            scan.skipped_illiquid += 1
            continue
        scan.checked += 1
        for fn in chosen.values():
            try:
                hit = fn(ticker, name, prices, rules)
            except Exception as exc:
                scan.warnings.append(f"{ticker}: {exc}")
                continue
            if hit is not None:
                scan.setups.append(hit)
    print(" " * 50, end="\r", file=sys.stderr)

    store = SeenStore(cfg.get("market_state_file", ".cache/tracker_market_seen.json"))
    fresh = [s for s in scan.setups if store.is_new_key(s.key)]
    shown = sorted(scan.setups if a.all else fresh, key=lambda s: -s.strength)[: a.top]

    title = (f"Skan rynku {scan.run_date} — {len(shown)} {'łącznie' if a.all else 'nowych'} setupów "
             f"({scan.checked} płynnych z {len(symbols)}; pominięto {scan.skipped_illiquid} mało płynnych)")
    print(title)
    if shown:
        print(report.table(["Ticker", "Nazwa", "Kurs", "Obrót/dzień", "Sygnał", "Szczegóły"], [[
            s.ticker, s.name[:28], f"{s.last_close:.2f}", fmt.usd(s.avg_dollar_volume), s.headline, s.detail,
        ] for s in shown], right={2, 3}))
    else:
        print("  Nic nowego nie spełnia reguł.")

    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"market_{scan.run_date}.json").write_text(json.dumps({
        "run_date": scan.run_date, "checked": scan.checked, "skipped_illiquid": scan.skipped_illiquid,
        "setups": [s.__dict__ for s in shown], "warnings": scan.warnings[:50],
    }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if a.discord and shown:
        lines = [f"**{title}**"] + [f"🎯 **{s.ticker}** {s.headline}\n   {s.name} — {s.detail}" for s in shown]
        try:
            sent = send_discord("\n".join(lines))
            print("Discord: wysłano" if sent else "Discord: brak DISCORD_WEBHOOK_URL", file=sys.stderr)
        except Exception as exc:
            print(f"Discord: błąd ({exc})", file=sys.stderr)

    for s in scan.setups:
        store.remember_key(s.key)
    store.save()
    if scan.warnings:
        print(f"\n{len(scan.warnings)} symboli z błędami (pierwsze 5): " + "; ".join(scan.warnings[:5]), file=sys.stderr)
    return 0


def _cmd_dump(ctx: Context) -> int:
    """Print real price history as CSV so a session without network can keep it
    under data/samples/ and replay rules on it (provider 'samples')."""
    for raw in ctx.args.symbols:
        symbol = normalise_symbol(raw)
        prices = ctx.provider.get_prices(symbol, ctx.args.days)
        if prices is None or prices.empty:
            print(f"=== DUMP {symbol} EMPTY")
            continue
        print(f"=== DUMP {symbol} BEGIN {len(prices)}")
        print(prices.to_csv(float_format="%.6g", index_label="date").rstrip())
        print(f"=== DUMP {symbol} END")
    return 0


def _cmd_replay(ctx: Context) -> int:
    """Walk forward through history and show every day the rule would have fired.

    This is the acceptance test for a rule: run it on the symbol and date you
    found by hand and see whether the scanner would have found it too."""
    from .market import DEFAULTS, RULES

    a, cfg = ctx.args, ctx.config
    rules = {**DEFAULTS, **(cfg.get("market_rules") or {})}
    fn = RULES.get(a.rule)
    if fn is None:
        print(f"Nieznana reguła {a.rule!r}; dostępne: {', '.join(RULES)}", file=sys.stderr)
        return 1
    symbol = normalise_symbol(a.symbol)
    prices = ctx.provider.get_prices(symbol, max(int(cfg.get("lookback_days", 420)), a.days + 250))
    if prices is None or prices.empty:
        print(f"Brak notowań dla {symbol}.", file=sys.stderr)
        return 1

    n = len(prices)
    start = max(60, n - a.days)
    hits = []
    for k in range(start, n + 1):
        hit = fn(symbol, symbol, prices.iloc[:k], rules)
        if hit is not None:
            hits.append(hit)
    first, last = prices.index[start - 1].date(), prices.index[-1].date()
    print(f"{symbol} · reguła {a.rule} · {first} → {last} ({n - start + 1} sesji)")
    if not hits:
        print("  Reguła nie odpaliła ani razu w tym oknie.")
        return 0
    for h in hits:
        print(f"  {h.day}  kurs {h.last_close:.4g}  {h.headline}")
        print(f"             {h.detail}")
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
    print(f"  DISCORD_WEBHOOK    {'ustawiony' if os.environ.get('DISCORD_WEBHOOK_URL') else 'brak — alerty tylko w konsoli'}")
    print(f"  FTP (publish.py)   {'ustawiony' if os.environ.get('FTP_HOST') else 'brak — stronę wgrywasz ręcznie'}")
    print(f"  źródło transakcji  {ctx.feed.name}")
    print(f"  portfel            {len(ctx.portfolio())} pozycji")
    print(f"  obserwowane        {len(ctx.watchlist())} symboli")
    funds = load_funds(ctx.config.get("funds", "data/funds_13f.csv"))
    print(f"  fundusze 13F       {', '.join(f.key for f in funds)}")

    print("\nTest źródeł:")
    ok = True
    sec_ready = getattr(ctx.feed, "sec_ready", lambda: True)()
    if not sec_ready:
        print("  SEC lista spółek   pominięte (brak SEC_USER_AGENT)")
        print("  SEC Form 4 (NVDA)  pominięte (brak SEC_USER_AGENT)")
    else:
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
