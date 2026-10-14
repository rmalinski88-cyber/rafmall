"""`python -m screener trela`: score a universe on Trela's model and report it."""

from __future__ import annotations

import csv
import sys
from datetime import date
from html import escape
from pathlib import Path

from ..report import format as fmt
from .data import Readings, fetch_readings
from .scoring import CompanyScore, Model, load_model, score_universe

PILLAR_LABELS = {
    "growth": "Zyskowność",
    "fundamentals": "Fundamenty",
    "value": "Wycena",
    "must_have": "Must-have",
}


def run_trela(universe, model: Model, fetch, progress=None) -> tuple[list[CompanyScore], list, dict]:
    """Fetch readings for every ticker and score them. ``fetch(ticker) -> Readings``."""
    readings: dict[str, Readings] = {}
    tickers = [t for t in universe["ticker"] if t]
    for position, ticker in enumerate(tickers, start=1):
        if progress:
            progress(position, len(tickers), ticker)
        try:
            readings[ticker] = fetch(ticker)
        except Exception as exc:  # noqa: BLE001 - one bad ticker must not stop the run
            readings[ticker] = Readings(ticker=ticker, notes=[f"błąd pobierania: {exc}"])

    names = dict(zip(universe["ticker"], universe.get("name", universe["ticker"])))
    for ticker, r in readings.items():
        if names.get(ticker):
            r.name = names[ticker]

    scores, dropped = score_universe(
        {t: r.values for t, r in readings.items()},
        model,
        years_since_ipo={t: r.years_since_ipo for t, r in readings.items()},
    )
    return scores, dropped, readings


PT_RULES = ("pt_change_180d", "pt_drawdown_45d", "upside_vs_history")


def split_by_pt_data(scores: list[CompanyScore]) -> tuple[list[CompanyScore], list[CompanyScore]]:
    """``(full model, no price-target history)``.

    Trela's model is built for US listings; Yahoo has no analyst-target
    history for Tokyo, Seoul, Taipei or Hong Kong, so those companies cannot
    earn the 41 value points.  Mixing them into one list would rank them on
    missing data, so they get their own list, compared on the points they
    can earn.
    """
    full, partial = [], []
    for s in scores:
        (partial if all(s.readings.get(r) is None for r in PT_RULES) else full).append(s)
    partial.sort(key=lambda s: (s.flagged, -available_pct(s), s.ticker))
    return full, partial


def available_pct(s: CompanyScore) -> float:
    value_max = s.pillars.get("value", (0, 0))[1]
    available = s.max_total - value_max
    return (s.total / available) if available else 0.0


def render_console(scores, dropped, readings, model: Model, top: int | None = None) -> str:
    full, partial = split_by_pt_data(scores)
    out = [_render_block(full, dropped, readings, model, top, "PEŁNY MODEL (USA i spółki z historią ceny docelowej)")]
    if partial:
        out.append(_render_block(
            partial, [], readings, model, top,
            "BEZ HISTORII CENY DOCELOWEJ (giełdy azjatyckie i europejskie): wynik = punkty / maksimum bez wyceny",
            use_available=True,
        ))
    return "\n\n".join(out)


def _render_block(scores, dropped, readings, model: Model, top, title, use_available=False) -> str:
    active_max = scores[0].max_total if scores else model.max_points
    if use_available and scores:
        active_max -= scores[0].pillars.get("value", (0, 0))[1]
    lines = [
        f"=== {title} ===",
        f"{model.name} | {date.today().isoformat()} | spółek: {len(scores)} | maksimum: {active_max:g} pkt",
    ]
    if dropped:
        lines.append(
            "Reguły bez danych u źródła (wyłączone z maksimum): "
            + ", ".join(f"{r.nazwa} ({r.max:g})" for r in dropped)
        )
    header = f"{'#':>3}  {'Ticker':<10}{'Spółka':<28}{'Wynik':>7}  {'Zysk.':>7}  {'Fund.':>7}  {'Wycena':>7}  {'MH':>3}  Uwagi"
    lines += ["", header, "-" * len(header)]
    shown = scores if top is None else scores[:top]
    for i, s in enumerate(shown, start=1):
        r = readings[s.ticker]
        g, f, v, m = (s.pillars.get(p, (0, 0)) for p in ("growth", "fundamentals", "value", "must_have"))
        note = "FLAGA: " + "; ".join(s.flags) if s.flags else (f"brak: {len(s.missing)}" if s.missing else "")
        shown_pct = available_pct(s) if use_available else s.pct
        lines.append(
            f"{i:>3}  {s.ticker:<10}{(r.name or s.ticker)[:27]:<28}{shown_pct * 100:>6.1f}%  "
            f"{g[0]:>4.1f}/{g[1]:<2g} {f[0]:>4.1f}/{f[1]:<2g} {v[0]:>4.1f}/{v[1]:<2g}  {m[0]:>1.0f}/{m[1]:g}  {note}"
        )
    if not use_available:
        lines += ["", "Zielony >= 70%, czerwony < 40% (jak w Scrab). Model Treli to podpowiedź do ręcznego",
                  "przeglądu TOP 50, nie rekomendacja inwestycyjna."]
    return "\n".join(lines)


def write_csv(scores, readings, model: Model, path: Path) -> None:
    rule_ids = [r.id for r in model.rules]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["pozycja", "ticker", "nazwa", "wynik_pct", "excel_pct", "punkty", "maksimum",
                         "flagi", "braki", "upside_teraz", *[f"odczyt_{i}" for i in rule_ids],
                         *[f"pkt_{i}" for i in rule_ids], "uwagi"])
        for i, s in enumerate(scores, start=1):
            r = readings[s.ticker]
            writer.writerow([
                i, s.ticker, r.name, round(s.pct * 100, 2), round(s.excel_pct * 100, 2),
                round(s.total, 2), s.max_total, " | ".join(s.flags), " ".join(s.missing),
                _round(r.upside_now),
                *[_round(s.readings.get(rid)) for rid in rule_ids],
                *[_round(s.points.get(rid)) for rid in rule_ids],
                " | ".join(r.notes),
            ])


def _round(value):
    return "" if value is None else round(float(value), 4)


def write_html(scores, dropped, readings, model: Model, path: Path) -> None:
    full, partial = split_by_pt_data(scores)
    tables = _html_table(full, readings, model, use_available=False)
    if partial:
        tables += (
            "<h2>Bez historii ceny docelowej</h2><p class='note'>Giełdy azjatyckie i europejskie: Yahoo nie publikuje "
            "dla nich historii cen docelowych analityków, więc reguły wyceny (41 pkt) nie mają danych. Wynik = punkty / "
            "maksimum bez wyceny – porównuj te spółki między sobą, nie z listą wyżej. Trela stosuje model tylko do giełd USA.</p>"
            + _html_table(partial, readings, model, use_available=True)
        )
    _write_page(scores, dropped, model, tables, path)


def _html_table(scores, readings, model: Model, use_available: bool) -> str:
    rows = []
    for i, s in enumerate(scores, start=1):
        r = readings[s.ticker]
        shown = available_pct(s) if use_available else s.pct
        state = "flag" if s.flagged else ("green" if shown >= model.green else ("red" if shown < model.red else "mid"))
        cells = "".join(
            f'<td class="num">{s.pillars[p][0]:.1f}<span class="sub">/{s.pillars[p][1]:g}</span></td>'
            for p in ("growth", "fundamentals", "value", "must_have")
        )
        detail = "".join(
            f"<li>{escape(rule.nazwa)}: <b>{_fmt_points(s.points.get(rule.id))}</b> / {rule.max:g} "
            f"<span class='sub'>(odczyt {escape(_fmt_reading(rule.id, s.readings.get(rule.id)))})</span></li>"
            for rule in model.rules if rule.id in s.points
        )
        notes = "".join(f"<li>{escape(n)}</li>" for n in r.notes)
        flags = f"<div class='flags'>⚑ {escape('; '.join(s.flags))}</div>" if s.flags else ""
        rows.append(
            f"<tr class='{state}'><td class='num'>{i}</td>"
            f"<td><b>{escape(r.name or s.ticker)}</b><div class='sub'>{escape(s.ticker)}</div>{flags}</td>"
            f"<td class='num score'>{shown * 100:.1f}%</td>{cells}"
            f"<td class='num'>{fmt.pct(r.upside_now, signed=True)}</td>"
            f"<td><details><summary>{len(s.missing)} braków</summary><ul>{detail}</ul>"
            f"{'<ul class=sub>' + notes + '</ul>' if notes else ''}</details></td></tr>"
        )
    return (
        '<div class="scroll"><table><thead><tr><th>#</th><th>Spółka</th><th class="num">Wynik</th>'
        '<th class="num">Zyskowność</th><th class="num">Fundamenty</th><th class="num">Wycena</th>'
        '<th class="num">Must-have</th><th class="num">Upside</th><th>Szczegóły</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _write_page(scores, dropped, model: Model, tables: str, path: Path) -> None:
    dropped_html = (
        "<p class='note'>Wyłączone z maksimum (źródło nie publikuje tych danych): "
        + ", ".join(f"{escape(r.nazwa)} ({r.max:g} pkt)" for r in dropped) + "</p>"
        if dropped else ""
    )
    max_total = scores[0].max_total if scores else model.max_points
    html = f"""<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Model Treli</title>
<style>
:root{{--bg:#f9f9f7;--card:#fcfcfb;--fg:#0b0b0b;--sub:#52514e;--muted:#898781;--line:#e1e0d9;
--good:#0ca30c;--bad:#d03b3b;--warn:#fab219}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d0d0d;--card:#1a1a19;--fg:#fff;--sub:#c3c2b7;--line:#2c2c2a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
.wrap{{max-width:1200px;margin:0 auto;padding:28px 16px 64px}}
h1{{font-size:1.5rem;margin:0 0 4px}} h2{{font-size:1.1rem;margin:32px 0 4px}} .note{{color:var(--sub);font-size:.88rem}}
.scroll{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;margin-top:18px}}
table{{border-collapse:collapse;width:100%;font-size:.86rem}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{color:var(--sub);font-size:.74rem;text-transform:uppercase;letter-spacing:.03em}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.sub{{color:var(--muted);font-size:.78rem}} .score{{font-weight:700}}
tr.green .score{{color:var(--good)}} tr.red .score{{color:var(--bad)}} tr.flag{{opacity:.6}}
.flags{{color:var(--bad);font-size:.78rem}} details ul{{margin:6px 0;padding-left:18px}}
</style></head><body><div class="wrap">
<h1>{escape(model.name)}</h1>
<p class="note">{date.today().isoformat()} · {len(scores)} spółek · maksimum {max_total:g} pkt ·
wynik = suma punktów / maksimum (jak w Scrab); zielony ≥ {model.green:.0%}, czerwony &lt; {model.red:.0%}.
Spółki z flagą Must-have są na końcu listy.</p>{dropped_html}
{tables}
<p class="note">Metoda: kurs Tomasza Treli (Uniwersytet Inwestycyjny 2026), model finalny ze spotkań 8 i 10.
Dane: Yahoo Finance. Prognozy na 2 lata = średnia geometryczna prognoz na bieżący i następny rok obrotowy;
zmiana w 5 lat przeliczona ze średniorocznego tempa, gdy sprawozdań jest mniej; cena docelowa odtworzona
z historii rekomendacji analityków. To podpowiedź do ręcznego przeglądu, nie rekomendacja inwestycyjna.</p>
</div></body></html>"""
    path.write_text(html, encoding="utf-8")


def _fmt_points(value) -> str:
    return "—" if value is None else f"{value:.1f}"


_PCT_RULES = {"revenue_5y", "revenue_est_2y", "eps_5y", "eps_est_2y", "eps_est_5y", "cfo_5y",
              "cfo_est_2y", "ebitda_margin", "pt_change_180d", "pt_drawdown_45d"}


def _fmt_reading(rule_id: str, value) -> str:
    if value is None:
        return "brak"
    if rule_id in _PCT_RULES:
        return fmt.pct(value, signed=True)
    if rule_id == "market_cap":
        return fmt.usd(value)
    if rule_id == "upside_vs_history":
        return f"{value * 100:.0f}% kanału"
    return fmt.num(value, 2)


def cmd_trela(args, config, universe) -> int:
    """Entry point wired into ``screener.cli``."""
    from ..cache import Cache
    from ..providers.yahoo import YahooProvider

    model = load_model(getattr(args, "model", None) or "config/trela.yml")
    fx_source = YahooProvider(cache=Cache(config.get("cache_dir", ".cache"), config.get("cache_ttl_hours", 12)))

    def progress(position, total, ticker):
        print(f"  [{position}/{total}] {ticker}", file=sys.stderr, flush=True)

    scores, dropped, readings = run_trela(
        universe, model, lambda t: fetch_readings(t, fx_source.get_fx_to_usd), progress=progress
    )
    print(render_console(scores, dropped, readings, model, top=getattr(args, "top", None)))

    out_dir = Path(getattr(args, "out_dir", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    write_csv(scores, readings, model, out_dir / f"trela_{stamp}.csv")
    write_html(scores, dropped, readings, model, out_dir / f"trela_{stamp}.html")
    print(f"\nCSV:  {out_dir / f'trela_{stamp}.csv'}\nHTML: {out_dir / f'trela_{stamp}.html'}", file=sys.stderr)
    return 0
