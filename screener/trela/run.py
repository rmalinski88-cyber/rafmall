"""`python -m screener trela`: score a universe on Trela's model and report it."""

from __future__ import annotations

import csv
import sys
import threading
import time
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd

from ..providers.tradingview import tradingview_url
from ..report import format as fmt
from .data import Readings, fetch_readings
from .scoring import CompanyScore, Model, load_model, score_universe

PILLAR_LABELS = {
    "growth": "Zyskowność",
    "fundamentals": "Fundamenty",
    "value": "Wycena",
    "must_have": "Must-have",
}


def run_trela(universe, model: Model, fetch, progress=None, workers: int = 1,
              prefilter: bool = False) -> tuple[list[CompanyScore], list, dict]:
    """Fetch readings for every ticker and score them. ``fetch(ticker) -> Readings``.

    With ``prefilter`` the model's loose screener runs first; companies it
    cuts stay in ``readings`` (``Readings.prefiltr`` says why) but are not
    ranked.  Humanoid-tagged companies are never cut - the user wants to see
    them even when the model flags them.
    """
    tickers = [t for t in universe["ticker"] if t]
    readings = _fetch_all(tickers, fetch, progress, workers)

    names = dict(zip(universe["ticker"], universe.get("name", universe["ticker"])))
    humanoid = dict(zip(universe["ticker"], universe["humanoid"])) if "humanoid" in universe else {}
    exchanges = dict(zip(universe["ticker"], universe["exchange"])) if "exchange" in universe else {}
    for ticker, r in readings.items():
        if isinstance(exchanges.get(ticker), str):
            r.exchange = exchanges[ticker]
        if names.get(ticker) and names[ticker] != ticker:
            r.name = names[ticker]
        r.humanoid = bool(humanoid.get(ticker, False))
        if r.humanoid:
            r.prefiltr = ""
        elif prefilter and not r.prefiltr:
            r.prefiltr = prefilter_reason(r.values, model.prefilter)

    # A fetch that returned nothing is not ranked at all: 0% would read as a
    # verdict on the company.  The report lists these separately.
    ranked = {t: r for t, r in readings.items() if not r.prefiltr and not r.empty}
    scores, dropped = score_universe(
        {t: r.values for t, r in ranked.items()},
        model,
        years_since_ipo={t: r.years_since_ipo for t, r in ranked.items()},
    )
    return scores, dropped, readings


def _fetch_all(tickers, fetch, progress, workers: int) -> dict[str, Readings]:
    def one(ticker):
        try:
            return fetch(ticker)
        except Exception as exc:  # noqa: BLE001 - one bad ticker must not stop the run
            return Readings(ticker=ticker, notes=[f"błąd pobierania: {exc}"])

    readings: dict[str, Readings] = {}
    if workers <= 1:
        for position, ticker in enumerate(tickers, start=1):
            if progress:
                progress(position, len(tickers), ticker)
            readings[ticker] = one(ticker)
        return readings

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, t): t for t in tickers}
        for position, future in enumerate(as_completed(futures), start=1):
            ticker = futures[future]
            readings[ticker] = future.result()
            if progress:
                progress(position, len(tickers), ticker)
    return {t: readings[t] for t in tickers}


_THROTTLE = threading.Lock()


def fetch_with_retry(fetch, pauses=(20, 60), sleep=time.sleep) -> Readings:
    """Retry a fetch that came back empty: Yahoo answers a burst of requests
    with 401/429 for a while and then recovers.  The lock spaces the retries
    out so they do not arrive as another burst."""
    result = fetch()
    for pause in pauses:
        if not result.empty:
            break
        with _THROTTLE:
            sleep(pause)
        result = fetch()
    return result


def prefilter_reason(values: dict, minimums: dict) -> str:
    """Why Trela's screener would not list the company; ``""`` when it passes.

    A missing reading never cuts: an empty Yahoo table is not evidence
    against the company, and the model scores a missing reading 0 anyway.
    """
    failed = []
    for rule_id, minimum in minimums.items():
        value = values.get(rule_id)
        if value is None or (isinstance(value, float) and value != value):
            continue
        if value < minimum:
            failed.append(f"{_PREFILTER_LABELS.get(rule_id, rule_id)} {_fmt_reading(rule_id, value)}"
                          f" < {_fmt_reading(rule_id, minimum)}")
    return "; ".join(failed)


_PREFILTER_LABELS = {
    "market_cap": "kapitalizacja",
    "revenue_est_2y": "prognoza przychodów",
    "eps_est_2y": "prognoza EPS",
    "eps_ttm": "EPS",
    "altman": "Altman",
}


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
        (full if has_value_history(s) else partial).append(s)
    partial.sort(key=lambda s: (s.flagged, -available_pct(s), s.ticker))
    return full, partial


def has_value_history(s: CompanyScore) -> bool:
    """Target history long enough for the big value rules (40 of 41 points).

    The 45-day drawdown alone (TradingView history grows from the first
    snapshot) flags a cut but does not make the value pillar comparable.
    """
    return any(s.readings.get(r) is not None for r in ("pt_change_180d", "upside_vs_history"))


def available_pct(s: CompanyScore) -> float:
    value_got, value_max = s.pillars.get("value", (0, 0))
    available = s.max_total - value_max
    return ((s.total - value_got) / available) if available else 0.0


PT_MISSING_WARN = 0.30   # above this share without target history the Value pillar is not trustworthy


def run_summary(scores, readings, source: str = "") -> list[str]:
    """Lines that say what the ranking stands on: source, screener cut, data gaps."""
    lines = []
    if source:
        lines.append(f"Uniwersum: {source}.")
    cut = [r for r in readings.values() if r.prefiltr]
    failed = failed_fetches(readings)
    if cut or failed:
        lines.append(f"Sprawdzono {len(readings)} spółek; filtr wstępny Treli odrzucił {len(cut)}, "
                     f"bez danych z Yahoo {len(failed)}, w rankingu {len(scores)}.")
    if failed and len(failed) > 0.1 * len(readings):
        lines.append(f"UWAGA: Yahoo nie zwróciło danych dla {len(failed)} spółek (limit zapytań?) — "
                     "ich nie ma w rankingu; powtórz przebieg później.")
    if scores:
        no_pt = sum(1 for s in scores if not has_value_history(s))
        if no_pt / len(scores) > PT_MISSING_WARN:
            lines.append(f"UWAGA: {no_pt} z {len(scores)} spółek bez historii cen docelowych z Yahoo — "
                         "filar Wycena (41 pkt) jest dla nich pusty, ranking mniej wiarygodny.")
    return lines


def failed_fetches(readings) -> list[Readings]:
    return [r for r in readings.values() if r.empty and not r.prefiltr]


def humanoid_positions(scores) -> list[tuple[int, CompanyScore]]:
    return [(i, s) for i, s in enumerate(scores, start=1) if s.humanoid]


def render_console(scores, dropped, readings, model: Model, top: int | None = None, source: str = "") -> str:
    for s in scores:
        s.humanoid = readings[s.ticker].humanoid
    full, partial = split_by_pt_data(scores)
    summary = run_summary(scores, readings, source)
    out = ["\n".join(summary)] if summary else []
    out.append(_render_block(full, dropped, readings, model, top, "PEŁNY MODEL (USA i spółki z historią ceny docelowej)"))
    tagged = humanoid_positions(full)
    if tagged:
        out.append("Spółki humanoidalne w rankingu: " + ", ".join(
            f"{s.ticker} #{i} ({s.pct * 100:.0f}%{', flaga' if s.flagged else ''})" for i, s in tagged))
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
        if r.upside_now is not None and r.upside_now <= 0:
            note = ("cena ≥ cel analityków — nie kupuj teraz; " + note).rstrip("; ")
        if r.humanoid:
            note = ("[H] " + note).rstrip()
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
                         "flagi", "braki", "upside_teraz", "humanoid", *[f"odczyt_{i}" for i in rule_ids],
                         *[f"pkt_{i}" for i in rule_ids], "uwagi", "lata_od_ipo", "cena_docelowa", "gielda",
                         "tradingview"])
        for i, s in enumerate(scores, start=1):
            r = readings[s.ticker]
            writer.writerow([
                i, s.ticker, r.name, round(s.pct * 100, 2), round(s.excel_pct * 100, 2),
                round(s.total, 2), s.max_total, " | ".join(s.flags), " ".join(s.missing),
                _round(r.upside_now), int(r.humanoid),
                *[_round(s.readings.get(rid)) for rid in rule_ids],
                *[_round(s.points.get(rid)) for rid in rule_ids],
                " | ".join(r.notes), _round(r.years_since_ipo), _round(r.price_target),
                r.exchange, tradingview_url(s.ticker, r.exchange),
            ])
        for r in readings.values():
            if r.prefiltr or r.empty:
                flag = f"{PREFILTER_MARK}{r.prefiltr}" if r.prefiltr else "brak danych z Yahoo"
                writer.writerow(["", r.ticker, r.name, "", "", "", "", flag, "",
                                 _round(r.upside_now), int(r.humanoid),
                                 *[_round(r.values.get(rid)) for rid in rule_ids],
                                 *["" for _ in rule_ids], " | ".join(r.notes),
                                 _round(r.years_since_ipo), _round(r.price_target),
                                 r.exchange, tradingview_url(r.ticker, r.exchange)])


PREFILTER_MARK = "filtr wstępny: "


def read_csv_readings(path: Path, model: Model) -> tuple[pd.DataFrame, dict[str, Readings]]:
    """``(universe, readings)`` back from a report CSV, so a report can be
    rebuilt without fetching again (e.g. from a CSV printed in an Actions log)."""
    readings: dict[str, Readings] = {}
    with Path(path).open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            values = {r.id: _float(row.get(f"odczyt_{r.id}")) for r in model.rules}
            flags = row.get("flagi") or ""
            readings[row["ticker"]] = Readings(
                ticker=row["ticker"], name=row.get("nazwa") or row["ticker"], values=values,
                notes=[n for n in (row.get("uwagi") or "").split(" | ") if n],
                years_since_ipo=_float(row.get("lata_od_ipo")),
                upside_now=_float(row.get("upside_teraz")),
                price_target=_float(row.get("cena_docelowa")),
                humanoid=row.get("humanoid") == "1",
                prefiltr=flags[len(PREFILTER_MARK):] if flags.startswith(PREFILTER_MARK) else "",
                exchange=row.get("gielda") or "",
            )
    universe = pd.DataFrame({
        "ticker": list(readings), "name": [r.name for r in readings.values()],
        "humanoid": [r.humanoid for r in readings.values()],
        "exchange": [r.exchange for r in readings.values()],
    })
    return universe, readings


def _float(text):
    try:
        return float(text) if text not in (None, "") else None
    except ValueError:
        return None


def _round(value):
    return "" if value is None else round(float(value), 6)


def write_html(scores, dropped, readings, model: Model, path: Path, source: str = "") -> None:
    for s in scores:
        s.humanoid = readings[s.ticker].humanoid
    full, partial = split_by_pt_data(scores)
    summary = "".join(
        f"<p class='note{' warn' if line.startswith('UWAGA') else ''}'>{escape(line)}</p>"
        for line in run_summary(scores, readings, source)
    )
    tagged = humanoid_positions(full)
    tables = summary
    if tagged:
        tables += ("<h2>Twoje spółki humanoidalne</h2><p class='note'>Pozycje w pełnym rankingu poniżej. "
                   "Nie przechodzą przez filtr wstępny, więc widać je nawet z flagą.</p>"
                   + _html_table([s for _, s in tagged], readings, model, use_available=False,
                                 positions=[i for i, _ in tagged]))
        tables += "<h2>Cały ranking</h2>"
    tables += _html_table(full, readings, model, use_available=False)
    if partial:
        tables += (
            "<h2>Bez historii ceny docelowej</h2><p class='note'>Giełdy azjatyckie i europejskie: Yahoo nie publikuje "
            "dla nich historii cen docelowych analityków, więc reguły wyceny (41 pkt) nie mają danych. Wynik = punkty / "
            "maksimum bez wyceny – porównuj te spółki między sobą, nie z listą wyżej. Trela stosuje model tylko do giełd USA.</p>"
            + _html_table(partial, readings, model, use_available=True)
        )
    failed = failed_fetches(readings)
    if failed:
        tables += (f"<h2>Bez danych z Yahoo ({len(failed)})</h2><p class='note'>Nie oceniane — brak odpowiedzi "
                   "źródła to nie ocena spółki.</p><p class='note'>"
                   + escape(", ".join(r.ticker for r in failed)) + "</p>")
    cut = [r for r in readings.values() if r.prefiltr]
    if cut:
        items = "".join(f"<li><b>{_tv_link(r.ticker, r.exchange)}</b> {escape(r.name or '')}: "
                        f"<span class='sub'>{escape(r.prefiltr)}</span></li>" for r in cut)
        tables += (f"<h2>Odrzucone przez filtr wstępny ({len(cut)})</h2><details><summary>pokaż</summary>"
                   f"<ul class='note'>{items}</ul></details>")
    _write_page(scores, dropped, model, tables, path)


def _html_table(scores, readings, model: Model, use_available: bool, positions=None) -> str:
    rows = []
    for i, s in zip(positions or range(1, len(scores) + 1), scores):
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
        tag = " <span class='tag'>humanoidy</span>" if r.humanoid else ""
        above = r.upside_now is not None and r.upside_now <= 0
        upside = (f"<td class='num bad' title='cena ≥ cel analityków — nie kupuj teraz'>"
                  f"{fmt.pct(r.upside_now, signed=True)}<div class='sub'>nie kupuj teraz</div></td>"
                  if above else f"<td class='num'>{fmt.pct(r.upside_now, signed=True)}</td>")
        rows.append(
            f"<tr class='{state}'><td class='num'>{i}</td>"
            f"<td><b>{escape(r.name or s.ticker)}</b>{tag}<div class='sub'>{_tv_link(s.ticker, r.exchange)}</div>{flags}</td>"
            f"<td class='num score'>{shown * 100:.1f}%</td>{cells}{upside}"
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
    max_total = max((s.max_total for s in scores), default=model.max_points)
    html = f"""<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Model Treli</title>
<style>
:root{{--bg:#f9f9f7;--card:#fcfcfb;--fg:#0b0b0b;--sub:#52514e;--muted:#898781;--line:#e1e0d9;
--good:#0ca30c;--bad:#d03b3b;--warn:#fab219}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0d0d0d;--card:#1a1a19;--fg:#fff;--sub:#c3c2b7;--line:#2c2c2a}}}}
:root[data-theme="dark"]{{--bg:#0d0d0d;--card:#1a1a19;--fg:#fff;--sub:#c3c2b7;--line:#2c2c2a}}
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
.bad{{color:var(--bad)}} .warn{{color:var(--bad);font-weight:600}}
.tv{{color:inherit;text-decoration:underline dotted;text-underline-offset:2px}} .tv:hover{{text-decoration-style:solid}}
.tag{{font-size:.7rem;padding:1px 6px;border-radius:8px;border:1px solid var(--line);color:var(--sub);margin-left:6px}}
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


def _tv_link(ticker: str, exchange: str = "") -> str:
    return (f"<a class='tv' href='{escape(tradingview_url(ticker, exchange))}' target='_blank' rel='noopener' "
            f"title='Wykres w TradingView'>{escape(ticker)} ↗</a>")


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
    """Entry point wired into ``screener.cli``.

    Without an explicit universe file the run covers Trela's own universe:
    all US listings above 10 bn USD, through his loose screener.
    """
    from ..cache import Cache
    from ..providers.yahoo import YahooProvider
    from .universe import us_universe

    model = load_model(getattr(args, "model", None) or "config/trela.yml")
    fx_source = YahooProvider(cache=Cache(config.get("cache_dir", ".cache"), config.get("cache_ttl_hours", 12)))

    from_csv = getattr(args, "z_csv", None)
    if from_csv:
        universe, stored = read_csv_readings(Path(from_csv), model)
        source = f"odtworzone z {Path(from_csv).name} (bez ponownego pobierania)"
        fetch, prefilter = stored.__getitem__, False   # the stored cut (Readings.prefiltr) stays as it was
    else:
        if universe is None:
            universe, source = us_universe(model.prefilter.get("market_cap", 10e9))
            prefilter = True
        else:
            source, prefilter = f"plik ({len(universe)} spółek), bez filtra wstępnego", False

        targets = _tradingview_targets(universe, config, extra=getattr(args, "tylko_cele", False))
        if getattr(args, "tylko_cele", False):
            return 0   # daily snapshot only: the history is what the monthly run needs
        source += "; cele analityków bez historii u Yahoo (np. Azja): TradingView"

        def fetch(ticker):
            return targets.fill(fetch_with_retry(
                lambda: fetch_readings(ticker, fx_source.get_fx_to_usd,
                                       cut=(lambda v: prefilter_reason(v, model.prefilter)) if prefilter else None)))
    print(f"Model Treli: {len(universe)} spółek — {source}", file=sys.stderr)

    def progress(position, total, ticker):
        if position % 25 == 0 or position == total:
            print(f"  [{position}/{total}] {ticker}", file=sys.stderr, flush=True)

    scores, dropped, readings = run_trela(
        universe, model, fetch, progress=progress,
        workers=getattr(args, "workers", 2) or 1, prefilter=prefilter,
    )
    print(render_console(scores, dropped, readings, model, top=getattr(args, "top", None), source=source))

    out_dir = Path(getattr(args, "out_dir", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    write_csv(scores, readings, model, out_dir / f"trela_{stamp}.csv")
    write_html(scores, dropped, readings, model, out_dir / f"trela_{stamp}.html", source=source)
    print(f"\nCSV:  {out_dir / f'trela_{stamp}.csv'}\nHTML: {out_dir / f'trela_{stamp}.html'}", file=sys.stderr)

    if getattr(args, "discord", False):
        from tracker.notify import send_discord

        sent = send_discord(discord_summary(scores, readings, model, source))
        print("Discord: wysłano" if sent else "Discord: brak DISCORD_WEBHOOK_URL — nie wysłano", file=sys.stderr)
    return 0


def _tradingview_targets(universe, config, extra: bool = False):
    """Today's TradingView consensus for the universe, stored in the target history.

    ``extra`` (the daily snapshot job) also covers the humanoid list, so
    Asian names build their history between monthly runs.
    """
    from .targets import TargetHistory, TradingViewTargets
    from .universe import HUMANOID_LIST

    history = TargetHistory(Path(config.get("cache_dir", ".cache")) / "trela_cele.csv")
    targets = TradingViewTargets(history)
    tickers = list(universe["ticker"])
    exchanges = {}
    if "exchange" in universe:
        exchanges = {t: e for t, e in zip(universe["ticker"], universe["exchange"]) if isinstance(e, str)}
    if extra:
        try:
            tickers += [t for t in pd.read_csv(HUMANOID_LIST, comment="#")["ticker"].dropna() if t not in tickers]
        except (OSError, ValueError):
            pass
    found = targets.prefetch(tickers, exchanges)
    history.save()
    print(f"TradingView: cele analityków dla {found} z {len(tickers)} spółek; historia celów: "
          f"{history.frame['date'].nunique()} dni, {history.frame['ticker'].nunique()} spółek "
          f"({history.path})", file=sys.stderr)
    for note in targets.notes:
        print(f"  {note}", file=sys.stderr)
    return targets


def discord_summary(scores, readings, model: Model, source: str = "", top: int = 15) -> str:
    """Short ranking for a Discord channel: top of the list and the humanoid names."""
    for s in scores:
        s.humanoid = readings[s.ticker].humanoid
    full, _ = split_by_pt_data(scores)
    lines = [f"**{model.name}** — {date.today().isoformat()}"]
    lines += run_summary(scores, readings, source)
    lines.append("")
    for i, s in enumerate([s for s in full if not s.flagged][:top], start=1):
        r = readings[s.ticker]
        upside = "" if r.upside_now is None else f", upside {r.upside_now * 100:+.0f}%"
        warn = " ⚠ cena ≥ cel" if r.upside_now is not None and r.upside_now <= 0 else ""
        # <url> keeps Discord from unfurling fifteen chart previews.
        lines.append(f"{i}. **[{s.ticker}](<{tradingview_url(s.ticker, r.exchange)}>)** {r.name} — "
                     f"{s.pct * 100:.1f}%{upside}{warn}")
    tagged = humanoid_positions(full)
    if tagged:
        lines += ["", "Humanoidy: " + ", ".join(
            f"{s.ticker} #{i} {s.pct * 100:.0f}%{' (flaga)' if s.flagged else ''}" for i, s in tagged)]
    lines += ["", "Podpowiedź do ręcznego przeglądu, nie rekomendacja."]
    return "\n".join(lines)