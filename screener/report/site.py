"""Static web page: the humanoid-robotics universe as a public-facing listing.

Unlike the analyst report, this is meant to be uploaded to a website: one
self-contained HTML file, grouped by segment, with a client-side filter and
search.  It reads the same ``ScreenResult`` the report does, so the numbers
on the site and in the report never disagree.
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from ..pipeline import ScreenResult
from . import format as fmt
from .charts import sparkline

TEMPLATE_DIR = Path(__file__).parent

SEGMENTS = [
    ("humanoid", "Humanoidy", "Spółki z własnym programem robota humanoidalnego."),
    ("komponenty", "Podzespoły", "Przekładnie, aktuatory, serwonapędy, czujniki, magnesy - to, z czego buduje się humanoida."),
    ("integrator", "Integratorzy", "Producenci gotowych robotów i automatyki, którzy mogą skalować produkcję humanoidów."),
    ("platforma/AI", "Platforma i AI", "Układy scalone, percepcja i modele sterujące robotem."),
    ("dywersyfikat", "Konglomeraty", "Duże grupy z istotnym, ale nie dominującym segmentem robotyki."),
]


def render_site(result: ScreenResult, output_path: str | Path, signals: dict | None = None,
                title: str = "Robotyka humanoidalna — spółki i dostawcy podzespołów") -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html"]))
    html = env.get_template("site.html").render(**build_site_context(result, signals, title))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build_site_context(result: ScreenResult, signals: dict | None, title: str) -> dict:
    import pandas as pd

    frame = pd.concat([result.ranked, result.rejected], ignore_index=True, sort=False)
    frame = frame.sort_values("composite_score", ascending=False, na_position="last")
    by_ticker = {s["ticker"]: s for s in (signals or {}).get("signals", [])}

    rows = [_row(record, result, by_ticker.get(record["ticker"])) for record in frame.to_dict("records")]
    segments = []
    for key, label, blurb in SEGMENTS:
        members = [r for r in rows if r["segment"] == key]
        if members:
            segments.append({"key": key, "label": label, "blurb": blurb, "rows": members})
    known = {s[0] for s in SEGMENTS}
    other = [r for r in rows if r["segment"] not in known]
    if other:
        segments.append({"key": "inne", "label": "Inne", "blurb": "", "rows": other})

    up = sum(1 for r in rows if r["ret_12m_value"] is not None and r["ret_12m_value"] > 0)
    return {
        "title": title,
        "run_date": result.run_date,
        "profile_name": result.profile_name,
        "count": len(rows),
        "segments": segments,
        "markets": sorted({r["market"] for r in rows if r["market"]}),
        "tiles": [
            {"label": "Spółek", "value": str(len(rows)), "sub": f"w {len(segments)} segmentach"},
            {"label": "Rok na plusie", "value": str(up), "sub": "kurs wyżej niż 12 mies. temu"},
            {"label": "W rankingu", "value": str(len(result.ranked)), "sub": "przeszły filtry płynności"},
            {"label": "Sygnały insiderów", "value": str(sum(1 for r in rows if r["signal"])),
             "sub": "spółek z transakcjami"},
        ],
        "dash": fmt.DASH,
        "data_json": Markup(json.dumps([{k: v for k, v in r.items() if k != "spark"} for r in rows],
                                       ensure_ascii=False).replace("</", "<\\/")),
    }


def _row(record: dict, result: ScreenResult, signal: dict | None) -> dict:
    ticker = record["ticker"]
    closes = result.prices.get(ticker)
    ret_12m = record.get("ret_12m")
    ret_12m = float(ret_12m) if ret_12m is not None and ret_12m == ret_12m else None
    score = record.get("composite_score")
    return {
        "ticker": ticker,
        "name": record.get("name") or ticker,
        "market": record.get("market") or "",
        "segment": record.get("segment") or "",
        "notes": record.get("notes") or "",
        "confidence": record.get("confidence") or "",
        "score": fmt.score(score),
        "score_value": float(score) if score is not None and score == score else None,
        "last_close": fmt.num(record.get("last_close"), 2),
        "currency": record.get("currency") or "",
        "market_cap": fmt.usd(record.get("market_cap_usd")),
        "ret_1m": fmt.pct(record.get("ret_1m"), signed=True),
        "ret_12m": fmt.pct(ret_12m, signed=True),
        "ret_12m_value": ret_12m,
        "px_vs_sma200": fmt.pct(record.get("px_vs_sma200"), signed=True),
        "rsi": fmt.num(record.get("rsi14"), 0),
        "pe": fmt.num(record.get("trailing_pe")),
        "revenue_growth": fmt.pct(record.get("revenue_growth"), signed=True),
        "excluded": record.get("excluded_reason") or "",
        "signal": (f"{signal['label']} ({signal['score']:+.1f})" if signal else ""),
        "signal_tone": ("good" if signal and signal["score"] >= 1 else "bad" if signal and signal["score"] <= -1
                        else "neutral") if signal else "",
        "spark": Markup(sparkline(closes.tail(252) if closes is not None else None)),
    }
