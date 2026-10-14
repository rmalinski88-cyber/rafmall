"""Trela's points model: linear scoring, must-have flags, total as in Scrab.

Pure functions only - no data fetching here, so every rule is testable on
hand-made numbers.

Rules (from the course notes, see ``config/trela.yml``):

* a reading at or below ``worst`` scores 0, at or above ``best`` scores the
  rule's maximum, in between proportionally;
* a must-have rule that scores 0 flags the company, which then goes to the
  end of the list regardless of its points;
* a missing reading scores 0 and is listed, but never flags or excludes a
  company ("Tolerance for Low Scores & Missing Data: Full");
* a rule with no reading for *any* company in the run cannot be computed
  from the available data at all, so it is dropped from the maximum rather
  than costing everyone the same points - the report names it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PILLARS = ("growth", "fundamentals", "value", "must_have")


@dataclass(frozen=True)
class Rule:
    id: str
    filar: str
    nazwa: str
    max: float
    worst: float
    best: float
    must_have: bool = False
    inclusive_worst: bool = False
    pewnosc: str = ""

    def points(self, value) -> float | None:
        """Linear points for ``value``; ``None`` when the reading is missing."""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        value = float(value)
        ascending = self.best >= self.worst
        if self.inclusive_worst and value == self.worst:
            return float(self.max)
        if ascending:
            if value <= self.worst:
                return 0.0
            if value >= self.best:
                return float(self.max)
        else:
            if value >= self.worst:
                return 0.0
            if value <= self.best:
                return float(self.max)
        return float(self.max) * (value - self.worst) / (self.best - self.worst)


@dataclass
class Model:
    name: str
    rules: list[Rule]
    min_years_since_ipo: float = 3.0
    green: float = 0.70
    red: float = 0.40

    @property
    def max_points(self) -> float:
        return sum(r.max for r in self.rules)

    def pillar_max(self, pillar: str, active: set[str] | None = None) -> float:
        return sum(r.max for r in self.rules if r.filar == pillar and (active is None or r.id in active))


def load_model(path: str | Path = "config/trela.yml") -> Model:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rules = []
    for raw in data["rules"]:
        fields = dict(raw)
        # PyYAML reads "10.0e9" (no exponent sign) as text; numbers must be numbers.
        for key in ("max", "worst", "best"):
            fields[key] = float(fields[key])
        rules.append(Rule(**fields))
    thresholds = data.get("thresholds") or {}
    return Model(
        name=data.get("name", "Model Treli"),
        rules=rules,
        min_years_since_ipo=float(data.get("min_years_since_ipo", 3)),
        green=float(thresholds.get("green", 0.70)),
        red=float(thresholds.get("red", 0.40)),
    )


@dataclass
class CompanyScore:
    ticker: str
    points: dict = field(default_factory=dict)       # rule id -> points or None
    readings: dict = field(default_factory=dict)     # rule id -> raw reading
    missing: list = field(default_factory=list)      # rule ids without a reading
    flags: list = field(default_factory=list)        # human-readable must-have failures
    total: float = 0.0
    max_total: float = 0.0
    pillars: dict = field(default_factory=dict)      # pillar -> (points, max)

    @property
    def pct(self) -> float:
        return self.total / self.max_total if self.max_total else 0.0

    @property
    def flagged(self) -> bool:
        return bool(self.flags)

    @property
    def excel_pct(self) -> float:
        """Excel variant: Growth, Fundamentals and Value as fractions of their max, averaged."""
        parts = [p / m for name, (p, m) in self.pillars.items() if name != "must_have" and m]
        return sum(parts) / len(parts) if parts else 0.0


def score_company(ticker: str, readings: dict, model: Model, active: set[str] | None = None,
                  years_since_ipo: float | None = None) -> CompanyScore:
    """Score one company on the rules in ``active`` (all rules when ``None``)."""
    result = CompanyScore(ticker=ticker)
    for rule in model.rules:
        if active is not None and rule.id not in active:
            continue
        value = readings.get(rule.id)
        pts = rule.points(value)
        result.readings[rule.id] = value
        result.points[rule.id] = pts
        result.max_total += rule.max
        if pts is None:
            result.missing.append(rule.id)
            continue
        result.total += pts
        if rule.must_have and pts == 0:
            result.flags.append(rule.nazwa)

    if years_since_ipo is not None and years_since_ipo < model.min_years_since_ipo:
        result.flags.append(f"mniej niż {model.min_years_since_ipo:g} lata od debiutu")

    for pillar in PILLARS:
        rules = [r for r in model.rules if r.filar == pillar and (active is None or r.id in active)]
        got = sum(result.points.get(r.id) or 0.0 for r in rules)
        result.pillars[pillar] = (got, sum(r.max for r in rules))
    return result


def score_universe(readings_by_ticker: dict, model: Model,
                   years_since_ipo: dict | None = None) -> tuple[list[CompanyScore], list[Rule]]:
    """Score every company; returns ``(ranked scores, rules dropped for lack of data)``.

    Ranking: unflagged companies by total (Scrab formula), then flagged ones,
    also by total - a flag sends a company to the end of the list.
    """
    years_since_ipo = years_since_ipo or {}
    dropped = [
        r for r in model.rules
        if all(_missing(readings.get(r.id)) for readings in readings_by_ticker.values())
    ]
    active = {r.id for r in model.rules} - {r.id for r in dropped}

    scores = [
        score_company(t, readings, model, active, years_since_ipo.get(t))
        for t, readings in readings_by_ticker.items()
    ]
    scores.sort(key=lambda s: (s.flagged, -s.pct, s.ticker))
    return scores, dropped


def _missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))
