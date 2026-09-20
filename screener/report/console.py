"""Plain-text ranking table for the terminal.

No ``rich`` dependency: the table is fixed-width and pipes cleanly into
``less``, ``grep`` or a file.
"""

from __future__ import annotations

import pandas as pd

from . import format as fmt

COLUMNS = [
    ("#", 3, "right"),
    ("Ticker", 10, "left"),
    ("Spółka", 26, "left"),
    ("Rynek", 9, "left"),
    ("Łącz.", 6, "right"),
    ("Fund.", 6, "right"),
    ("Tech.", 6, "right"),
    ("Pokr.", 6, "right"),
    ("Kapitaliz.", 12, "right"),
    ("Przych.", 9, "right"),
    ("ROE", 8, "right"),
    ("SMA200", 9, "right"),
    ("RS 6M", 9, "right"),
]


def _cell(text: str, width: int, align: str) -> str:
    text = str(text)
    if len(text) > width:
        text = text[: width - 1] + "…"
    return text.ljust(width) if align == "left" else text.rjust(width)


def _line(values, sep: str = "  ") -> str:
    return sep.join(_cell(v, w, a) for v, (_, w, a) in zip(values, COLUMNS))


def render_console(result, top: int | None = None) -> str:
    """Render the ranking (and a summary of exclusions) as text."""
    ranked = result.ranked if top is None else result.ranked.head(top)

    header = _line([name for name, _, _ in COLUMNS])
    out = [
        f"Screener robotyki humanoidalnej — Azja | {result.run_date}",
        f"profil: {result.profile_name} | źródło: {result.provider_name} | "
        f"w rankingu: {len(result.ranked)} z {result.screened_count}",
        "",
        header,
        "-" * len(header),
    ]

    if ranked.empty:
        out.append("(żadna spółka nie przeszła filtrów)")
    for position, record in enumerate(ranked.to_dict("records"), start=1):
        out.append(
            _line(
                [
                    position,
                    record["ticker"],
                    record.get("name") or record["ticker"],
                    record.get("market") or "",
                    fmt.score(record.get("composite_score")),
                    fmt.score(record.get("fundamental_score")),
                    fmt.score(record.get("technical_score")),
                    fmt.pct(record.get("fundamental_coverage"), digits=0),
                    fmt.usd(record.get("market_cap_usd")),
                    fmt.pct(record.get("revenue_growth"), signed=True),
                    fmt.pct(record.get("return_on_equity")),
                    fmt.pct(record.get("px_vs_sma200"), signed=True),
                    fmt.pct(record.get("rs_6m"), signed=True),
                ]
            )
        )

    out.extend(_exclusions(result.rejected))
    if result.warnings:
        out.append("")
        out.append(f"Ostrzeżenia ({len(result.warnings)}):")
        out.extend(f"  - {w}" for w in result.warnings[:12])
        if len(result.warnings) > 12:
            out.append(f"  ... i {len(result.warnings) - 12} więcej")

    out.append("")
    out.append("Wyniki są względne wobec tego uniwersum. To nie jest rekomendacja inwestycyjna.")
    return "\n".join(out)


def _exclusions(rejected: pd.DataFrame) -> list[str]:
    if rejected is None or rejected.empty:
        return []
    counts = rejected["excluded_reason"].value_counts()
    lines = ["", f"Odrzucone przez filtry: {len(rejected)}"]
    lines.extend(f"  {count:>3}x  {reason}" for reason, count in counts.items())
    return lines
