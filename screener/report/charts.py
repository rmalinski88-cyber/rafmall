"""Inline SVG chart builders for the HTML report.

Everything renders as static SVG with no JavaScript charting library: the
report has to open from a local file, offline, years from now.

Chart-design rules applied here (they are deliberate, not incidental):

* The scatter uses **one** series colour.  Market identity lives in the table
  column beside it - four categorical hues in an all-pairs form (every dot can
  sit next to every other) would not clear the colour-blind separation floor.
* Score bars use the two-slot categorical pair (blue / orange), which does
  clear it, and every bar carries a direct numeric label, so colour is never
  the only channel.
* Marks are thin, bars have 4px rounded outer ends anchored to the baseline,
  lines are 2px, dots are 10px across, and overlapping dots carry a 2px
  surface-coloured ring so a cluster stays countable.
* Axes and gridlines are hairlines in muted ink so the data stays dominant.
"""

from __future__ import annotations

from html import escape

import pandas as pd

# Roles are CSS custom properties defined once in the template, so light and
# dark modes swap in one place instead of being baked into every shape.
SURFACE = "var(--surface-1)"
SERIES_1 = "var(--series-1)"
SERIES_2 = "var(--series-2)"
GRID = "var(--gridline)"
AXIS = "var(--baseline)"
MUTED = "var(--text-muted)"


def sparkline(closes: pd.Series, width: int = 132, height: int = 34, pad: int = 3) -> str:
    """A 12-month price line: single series, no axes, no labels."""
    if closes is None or len(closes.dropna()) < 2:
        return f'<svg class="spark" width="{width}" height="{height}" role="img" aria-label="brak danych"></svg>'

    values = closes.dropna().astype(float)
    low, high = float(values.min()), float(values.max())
    span = (high - low) or 1.0

    inner_w, inner_h = width - 2 * pad, height - 2 * pad
    step = inner_w / (len(values) - 1)
    points = " ".join(
        f"{pad + i * step:.2f},{pad + inner_h - ((v - low) / span) * inner_h:.2f}"
        for i, v in enumerate(values)
    )

    first, last = float(values.iloc[0]), float(values.iloc[-1])
    change = (last / first - 1.0) if first else 0.0
    label = f"Zmiana w oknie: {change * 100:+.1f}%".replace(".", ",")
    end_y = pad + inner_h - ((last - low) / span) * inner_h

    return (
        f'<svg class="spark" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>"
        f'<polyline fill="none" stroke="{SERIES_1}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" points="{points}"/>'
        f'<circle cx="{width - pad:.2f}" cy="{end_y:.2f}" r="2.5" fill="{SERIES_1}"/>'
        "</svg>"
    )


def score_bar(value, width: int = 120, height: int = 10, series: str = SERIES_1) -> str:
    """A 0-100 magnitude bar anchored at zero, with a rounded data end."""
    if value is None or pd.isna(value):
        return f'<svg class="bar" width="{width}" height="{height}" role="img" aria-label="brak wyniku"></svg>'

    clamped = max(0.0, min(100.0, float(value)))
    filled = max(3.0, clamped / 100.0 * width)
    radius = min(4.0, filled / 2)

    return (
        f'<svg class="bar" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{clamped:.0f} na 100">'
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="{height/2:.1f}" fill="{GRID}"/>'
        f'<rect x="0" y="0" width="{filled:.2f}" height="{height}" rx="{radius:.1f}" fill="{series}"/>'
        "</svg>"
    )


def quadrant_scatter(
    frame: pd.DataFrame,
    label_top: int = 8,
    width: int = 720,
    height: int = 460,
) -> str:
    """Fundamental score (x) against technical score (y).

    The 50/50 crosshair splits the plane into the four readings that matter:
    strong on both, cheap-but-falling, momentum-without-substance, and weak on
    both.  Only the top names are direct-labelled - labelling all forty would
    be unreadable, and the table below carries the rest.
    """
    left, right, top, bottom = 56, 24, 34, 46
    plot_w, plot_h = width - left - right, height - top - bottom

    points = frame.dropna(subset=["fundamental_score", "technical_score"])
    if points.empty:
        return '<p class="empty">Brak spółek z kompletem wyników do wykresu.</p>'

    def sx(value: float) -> float:
        return left + (float(value) / 100.0) * plot_w

    def sy(value: float) -> float:
        return top + plot_h - (float(value) / 100.0) * plot_h

    parts = [
        f'<svg class="scatter" viewBox="0 0 {width} {height}" width="100%" '
        f'role="img" aria-label="Wynik fundamentalny wobec technicznego">'
    ]

    # Gridlines every 25 points, hairline, recessive.
    for tick in (0, 25, 50, 75, 100):
        x, y = sx(tick), sy(tick)
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 18}" text-anchor="middle" '
            f'class="tick">{tick}</text>'
        )
        parts.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" class="tick">{tick}</text>'
        )

    # The 50/50 split, drawn heavier than the grid because it carries meaning.
    parts.append(
        f'<line x1="{sx(50):.1f}" y1="{top}" x2="{sx(50):.1f}" y2="{top + plot_h}" '
        f'stroke="{AXIS}" stroke-width="1.5" stroke-dasharray="4 4"/>'
    )
    parts.append(
        f'<line x1="{left}" y1="{sy(50):.1f}" x2="{left + plot_w}" y2="{sy(50):.1f}" '
        f'stroke="{AXIS}" stroke-width="1.5" stroke-dasharray="4 4"/>'
    )

    quadrants = [
        (sx(75), sy(96), "mocne fundamenty + trend"),
        (sx(25), sy(96), "trend bez fundamentów"),
        (sx(75), sy(6), "fundamenty bez trendu"),
        (sx(25), sy(6), "słabe w obu wymiarach"),
    ]
    for x, y, text in quadrants:
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="quad">{escape(text)}</text>')

    ranked = points.sort_values("composite_score", ascending=False, na_position="last")
    labelled = set(ranked.head(label_top)["ticker"])

    for record in ranked.to_dict("records"):
        x, y = sx(record["fundamental_score"]), sy(record["technical_score"])
        tooltip = (
            f"{record.get('name') or record['ticker']} ({record['ticker']})\n"
            f"Fundamenty: {record['fundamental_score']:.0f} · "
            f"Technika: {record['technical_score']:.0f} · "
            f"Łącznie: {record.get('composite_score', float('nan')):.0f}"
        )
        # The surface-coloured ring keeps overlapping dots countable.
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{SERIES_1}" '
            f'stroke="{SURFACE}" stroke-width="2"><title>{escape(tooltip)}</title></circle>'
        )

    # Labels are drawn after every dot, so no dot can cover a label - and
    # every dot is an obstacle, so no label covers a neighbouring dot either.
    dots = [
        (sx(r["fundamental_score"]) - 7, sy(r["technical_score"]) - 7,
         sx(r["fundamental_score"]) + 7, sy(r["technical_score"]) + 7)
        for r in ranked.to_dict("records")
    ]
    placed: list[tuple[float, float, float, float]] = []
    for record in ranked.head(label_top).to_dict("records"):
        x, y = sx(record["fundamental_score"]), sy(record["technical_score"])
        ticker = str(record["ticker"])
        box = _place_label(
            x, y, ticker, placed + dots, left, left + plot_w, top, top + plot_h
        )
        if box is None:
            continue  # nowhere free: better unlabelled than overlapping
        label_x, label_y, anchor, rect = box
        placed.append(rect)
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" '
            f'class="point-label">{escape(ticker)}</text>'
        )

    parts.append(
        f'<text x="{left + plot_w / 2:.1f}" y="{height - 8}" text-anchor="middle" '
        f'class="axis-title">Wynik fundamentalny →</text>'
    )
    parts.append(
        f'<text transform="translate(16,{top + plot_h / 2:.1f}) rotate(-90)" '
        f'text-anchor="middle" class="axis-title">Wynik techniczny →</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


# Label geometry at the 11px bold size used by ``.point-label``.
_CHAR_WIDTH = 6.4
_LABEL_HEIGHT = 12.0

#: Candidate offsets, tried in order: right/left first, then further out.
_LABEL_OFFSETS = [
    (9, 4, "start"), (-9, 4, "end"),
    (9, -8, "start"), (-9, -8, "end"),
    (9, 15, "start"), (-9, 15, "end"),
    (0, -12, "middle"), (0, 20, "middle"),
    (9, -18, "start"), (-9, -18, "end"),
    (18, -22, "start"), (-18, -22, "end"),
    (18, 26, "start"), (-18, 26, "end"),
    (0, -24, "middle"), (0, 32, "middle"),
]


def _place_label(
    x: float,
    y: float,
    text: str,
    placed: list[tuple[float, float, float, float]],
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
):
    """First candidate position that hits neither a placed label nor an edge.

    Greedy rather than optimal, which is the right trade for eight labels:
    it is deterministic, and an unplaceable label is dropped instead of being
    drawn on top of another one.
    """
    width = len(text) * _CHAR_WIDTH

    for dx, dy, anchor in _LABEL_OFFSETS:
        label_x, label_y = x + dx, y + dy

        if anchor == "start":
            x0 = label_x
        elif anchor == "end":
            x0 = label_x - width
        else:
            x0 = label_x - width / 2
        rect = (x0, label_y - _LABEL_HEIGHT, x0 + width, label_y + 2)

        if rect[0] < min_x or rect[2] > max_x or rect[1] < min_y or rect[3] > max_y:
            continue
        if any(_overlaps(rect, other) for other in placed):
            continue
        return label_x, label_y, anchor, rect

    return None


def _overlaps(a, b, padding: float = 2.0) -> bool:
    return not (
        a[2] + padding < b[0]
        or b[2] + padding < a[0]
        or a[3] + padding < b[1]
        or b[3] + padding < a[1]
    )
