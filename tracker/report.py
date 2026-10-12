"""Console tables and the HTML dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from screener.report import format as fmt
from screener.report.charts import sparkline

from .amounts import format_range
from .models import CHANGE_LABELS, EXIT, HOLD, NEW, SIDE_LABELS, FundReport, Trade
from .signals import TickerSignal

TEMPLATE_DIR = Path(__file__).parent


@dataclass
class ScanResult:
    run_date: str
    feed_name: str
    congress: list[Trade]
    insiders: list[Trade]
    funds: list[FundReport]
    signals: list[TickerSignal]
    quotes: list[dict] = field(default_factory=list)
    new_keys: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)
    congress_days: int = 30
    insider_days: int = 30


# -- console -----------------------------------------------------------------


def table(headers: list[str], rows: list[list[str]], right: set[int] = frozenset()) -> str:
    if not rows:
        return "  (brak)"
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]

    def line(cells):
        return "  ".join(
            str(c).rjust(widths[i]) if i in right else str(c).ljust(widths[i])
            for i, c in enumerate(cells)
        ).rstrip()

    return "\n".join([line(headers), "  ".join("-" * w for w in widths), *(line(r) for r in rows)])


def trade_rows(trades: list[Trade], new_keys: set[str] = frozenset()) -> list[list[str]]:
    rows = []
    for t in sorted(trades, key=lambda t: (t.reported or date.min, t.traded or date.min), reverse=True):
        rows.append([
            "•" if t.key in new_keys else "",
            t.ticker,
            SIDE_LABELS.get(t.side, t.side) + (" (10b5-1)" if t.planned else ""),
            _clip(t.actor, 28),
            _clip(t.role, 26),
            format_range(t.amount_low, t.amount_high),
            str(t.traded or fmt.DASH),
            str(t.reported or fmt.DASH),
            fmt.DASH if t.lag_days is None else f"{t.lag_days} d",
        ])
    return rows


TRADE_HEADERS = ["", "Ticker", "Strona", "Kto", "Rola", "Kwota", "Transakcja", "Zgłoszenie", "Opóźn."]


def render_trades(title: str, trades: list[Trade], new_keys: set[str] = frozenset()) -> str:
    return f"\n{title} ({len(trades)})\n" + table(TRADE_HEADERS, trade_rows(trades, new_keys), right={5, 8})


def render_fund(report: FundReport, top: int = 15, show_hold: bool = False) -> str:
    f = report.fund
    head = (f"\n{f.name} — {f.manager}  |  stan na {report.period_now or '?'} "
            f"(zgłoszono {report.filed_now or '?'}), poprzednio {report.period_prev or '?'}  |  "
            f"portfel 13F: {fmt.usd(report.total_value)}")
    changes = [c for c in report.changes if show_hold or c.kind != HOLD][:top]
    rows = [[
        CHANGE_LABELS[c.kind],
        c.ticker or fmt.DASH,
        _clip(c.issuer, 30) + (f" [{c.put_call}]" if c.put_call else ""),
        fmt.usd(c.value_now if c.kind != EXIT else c.value_prev),
        fmt.pct(c.weight_now),
        fmt.pct(c.share_change, signed=True) if c.kind not in (NEW, EXIT) else fmt.DASH,
    ] for c in changes]
    return head + "\n" + table(["Zmiana", "Ticker", "Emitent", "Wartość", "Udział", "Δ akcji"], rows,
                               right={3, 4, 5})


def render_signals(signals: list[TickerSignal], top: int = 25) -> str:
    rows = []
    for s in signals[:top]:
        flag = "! " if s.alert else ("P " if s.in_portfolio else ("W " if s.on_watchlist else ""))
        rows.append([
            flag + s.ticker,
            f"{s.score:+.1f}",
            s.label,
            str(len(s.buyers)),
            str(len(s.sellers)),
            fmt.usd(s.buy_usd) if s.buy_usd else fmt.DASH,
            fmt.usd(s.sell_usd) if s.sell_usd else fmt.DASH,
            _clip("; ".join(s.reasons[:2]), 70),
        ])
    legend = "  (! = pozycja w portfelu z przewagą sprzedających, P = w portfelu, W = obserwowane)"
    return ("\nSYGNAŁY\n" + legend + "\n"
            + table(["Ticker", "Wynik", "Ocena", "Kup.", "Sprz.", "Kupno ~", "Sprzedaż ~", "Dlaczego"],
                    rows, right={1, 3, 4, 5, 6}))


def render_quote(card: dict) -> str:
    if card.get("error"):
        return f"\n{card['symbol']}: {card['error']}"
    size = (f"aktywa {fmt.usd(card.get('total_assets'))}" if card.get("total_assets")
            else f"kapitalizacja {fmt.usd(card.get('market_cap'))}")
    lines = [
        f"\n{card['name']}  ({card['symbol']})  — {card['asset_class']}"
        + (f", {card['category']}" if card.get("category") else "")
        + (f", {card['sector']}" if card.get("sector") else ""),
        f"Kurs: {fmt.num(card.get('last_close'), 2)} {card.get('currency') or ''}  |  {size}  |  trend: {card['trend']}",
        f"Zwrot 1M {fmt.pct(card.get('ret_1m'), signed=True)} · 3M {fmt.pct(card.get('ret_3m'), signed=True)} · "
        f"6M {fmt.pct(card.get('ret_6m'), signed=True)} · 12M {fmt.pct(card.get('ret_12m'), signed=True)}",
        f"RSI(14) {fmt.num(card.get('rsi14'), 0)} · vs SMA200 {fmt.pct(card.get('px_vs_sma200'), signed=True)} · "
        f"od szczytu 52T {fmt.pct(card.get('dist_52w_high'), signed=True)} · "
        f"RS 6M vs {card.get('benchmark') or '—'} {fmt.pct(card.get('rs_6m'), signed=True)} · "
        f"ATR {fmt.pct(card.get('atr_pct'))}",
    ]
    if card.get("trailing_pe") or card.get("forward_pe"):
        lines.append(f"C/Z {fmt.num(card.get('trailing_pe'))} · C/Z prognozowane {fmt.num(card.get('forward_pe'))} · "
                     f"wzrost przychodów {fmt.pct(card.get('revenue_growth'), signed=True)}")
    return "\n".join(lines)


def _clip(text: str, width: int) -> str:
    text = text or ""
    return text if len(text) <= width else text[: width - 1] + "…"


# -- html --------------------------------------------------------------------


def render_html(result: ScanResult, output_path: str | Path) -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html"]))
    html = env.get_template("template.html").render(**_context(result))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _context(r: ScanResult) -> dict:
    new_count = len(r.new_keys)
    buy = sum(1 for s in r.signals if s.score >= 1)
    sell = sum(1 for s in r.signals if s.score <= -1)
    alerts = [s for s in r.signals if s.alert]
    return {
        "run_date": r.run_date,
        "feed": r.feed_name,
        "congress_days": r.congress_days,
        "insider_days": r.insider_days,
        "tiles": [
            {"label": "Nowe transakcje", "value": str(new_count), "sub": "od poprzedniego skanu"},
            {"label": "Przewaga kupujących", "value": str(buy), "sub": "spółek z wynikiem ≥ +1"},
            {"label": "Przewaga sprzedających", "value": str(sell), "sub": "spółek z wynikiem ≤ −1"},
            {"label": "Alerty portfela", "value": str(len(alerts)),
             "sub": ", ".join(s.ticker for s in alerts) or "brak"},
        ],
        "signals": [{
            "ticker": s.ticker, "score": f"{s.score:+.1f}", "label": s.label,
            "tone": "good" if s.score >= 1 else "bad" if s.score <= -1 else "neutral",
            "buyers": len(s.buyers), "sellers": len(s.sellers),
            "buy_usd": fmt.usd(s.buy_usd) if s.buy_usd else fmt.DASH,
            "sell_usd": fmt.usd(s.sell_usd) if s.sell_usd else fmt.DASH,
            "reasons": s.reasons, "alert": s.alert, "in_portfolio": s.in_portfolio,
            "on_watchlist": s.on_watchlist,
        } for s in r.signals[:60]],
        "congress": _trade_ctx(r.congress, r.new_keys),
        "insiders": _trade_ctx(r.insiders, r.new_keys),
        "funds": [{
            "name": f.fund.name, "manager": f.fund.manager,
            "period": f.period_now, "prev": f.period_prev, "filed": f.filed_now,
            "total": fmt.usd(f.total_value),
            "rows": [{
                "kind": CHANGE_LABELS[c.kind], "tone": _change_tone(c.kind),
                "ticker": c.ticker or fmt.DASH, "issuer": c.issuer + (f" [{c.put_call}]" if c.put_call else ""),
                "value": fmt.usd(c.value_now if c.kind != EXIT else c.value_prev),
                "weight": fmt.pct(c.weight_now),
                "delta": fmt.pct(c.share_change, signed=True) if c.kind not in (NEW, EXIT) else fmt.DASH,
            } for c in f.changes if c.kind != HOLD][:20],
        } for f in r.funds],
        "quotes": [_quote_ctx(q) for q in r.quotes],
        "warnings": r.warnings,
        "dash": fmt.DASH,
    }


def _trade_ctx(trades: list[Trade], new_keys: set[str]) -> list[dict]:
    rows = []
    for t in sorted(trades, key=lambda t: (t.reported or date.min, t.traded or date.min), reverse=True)[:150]:
        rows.append({
            "new": t.key in new_keys, "ticker": t.ticker,
            "side": SIDE_LABELS.get(t.side, t.side), "tone": "good" if t.side == "buy" else "bad",
            "planned": t.planned, "actor": t.actor, "role": t.role,
            "amount": format_range(t.amount_low, t.amount_high),
            "traded": t.traded or fmt.DASH, "reported": t.reported or fmt.DASH,
            "lag": fmt.DASH if t.lag_days is None else f"{t.lag_days} d",
        })
    return rows


def _quote_ctx(q: dict) -> dict:
    if q.get("error"):
        return {"symbol": q["symbol"], "error": q["error"]}
    closes = q.get("closes")
    return {
        "symbol": q["symbol"], "name": q.get("name"), "kind": q.get("asset_class"),
        "last": fmt.num(q.get("last_close"), 2), "trend": q.get("trend"),
        "ret_1m": fmt.pct(q.get("ret_1m"), signed=True), "ret_12m": fmt.pct(q.get("ret_12m"), signed=True),
        "rsi": fmt.num(q.get("rsi14"), 0), "sma200": fmt.pct(q.get("px_vs_sma200"), signed=True),
        "spark": Markup(sparkline(closes.tail(252) if closes is not None else None)),
    }


def _change_tone(kind: str) -> str:
    return {"new": "good", "add": "good", "trim": "bad", "exit": "bad"}.get(kind, "neutral")
