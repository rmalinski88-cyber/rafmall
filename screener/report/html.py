"""HTML report rendering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from ..pipeline import ScreenResult
from . import format as fmt
from ..providers.tradingview import tradingview_url
from .charts import SERIES_1, SERIES_2, quadrant_scatter, score_bar, sparkline

TEMPLATE_DIR = Path(__file__).parent


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )


def render_html(result: ScreenResult, output_path: str | Path) -> Path:
    """Write the full report and return the path it landed at."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template = _environment().get_template("template.html")
    html = template.render(**build_context(result))
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build_context(result: ScreenResult) -> dict:
    """Assemble everything the template needs, already formatted."""
    ranked = result.ranked

    return {
        "run_date": result.run_date,
        "profile_name": result.profile_name,
        "provider_name": result.provider_name,
        "screened": result.screened_count,
        "dash": fmt.DASH,
        "tiles": _tiles(result),
        # Markup(): these strings are SVG we generated ourselves, not user input.
        "scatter_svg": Markup(quadrant_scatter(ranked) if not ranked.empty else ""),
        "rows": [_row(i, record, result) for i, record in enumerate(ranked.to_dict("records"), 1)],
        "rejected": _rejected(result.rejected),
        "warnings": result.warnings,
    }


def _tiles(result: ScreenResult) -> list[dict]:
    ranked = result.ranked
    passing = len(ranked)

    if passing:
        best = ranked.iloc[0]
        best_value = fmt.score(best.get("composite_score"))
        best_sub = f"{best.get('name') or best.get('ticker')}"
        above_both = int(
            (
                (ranked["fundamental_score"] >= 50) & (ranked["technical_score"] >= 50)
            ).fillna(False).sum()
        )
        median_coverage = fmt.pct(ranked["fundamental_coverage"].median(), digits=0)
    else:
        best_value, best_sub, above_both, median_coverage = fmt.DASH, "brak wyników", 0, fmt.DASH

    return [
        {"label": "W rankingu", "value": str(passing), "sub": f"z {result.screened_count} w uniwersum"},
        {"label": "Najwyższy wynik", "value": best_value, "sub": best_sub},
        {"label": "Mocne w obu wymiarach", "value": str(above_both), "sub": "fund. ≥ 50 i tech. ≥ 50"},
        {"label": "Mediana pokrycia danych", "value": median_coverage, "sub": "wskaźniki fundamentalne"},
    ]


def _row(position: int, record: dict, result: ScreenResult) -> dict:
    ticker = record["ticker"]
    closes = result.prices.get(ticker)
    window = closes.tail(252) if closes is not None else None

    return {
        "rank": position,
        "ticker": ticker,
        "tv_url": tradingview_url(ticker),
        "name": record.get("name") or ticker,
        "market": record.get("market") or fmt.DASH,
        "segment": record.get("segment") or fmt.DASH,
        "composite": fmt.score(record.get("composite_score")),
        "fundamental": fmt.score(record.get("fundamental_score")),
        "technical": fmt.score(record.get("technical_score")),
        "fund_bar": Markup(score_bar(record.get("fundamental_score"), series=SERIES_1)),
        "tech_bar": Markup(score_bar(record.get("technical_score"), series=SERIES_2)),
        "coverage": fmt.pct(record.get("fundamental_coverage"), digits=0),
        "market_cap": fmt.usd(record.get("market_cap_usd")),
        "revenue_growth": fmt.pct(record.get("revenue_growth"), signed=True),
        "operating_margin": fmt.pct(record.get("operating_margin")),
        "roe": fmt.pct(record.get("return_on_equity")),
        "pe": fmt.num(record.get("trailing_pe")),
        "px_vs_sma200": fmt.pct(record.get("px_vs_sma200"), signed=True),
        "rs_6m": fmt.pct(record.get("rs_6m"), signed=True),
        "rsi": fmt.num(record.get("rsi14"), digits=0),
        "spark": Markup(sparkline(window)),
    }


def _rejected(frame: pd.DataFrame) -> list[dict]:
    if frame is None or frame.empty:
        return []
    return [
        {
            "ticker": record["ticker"],
            "name": record.get("name") or record["ticker"],
            "market": record.get("market") or fmt.DASH,
            "reason": record.get("excluded_reason") or fmt.DASH,
        }
        for record in frame.to_dict("records")
    ]
