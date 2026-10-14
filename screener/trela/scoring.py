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
* a rule the data source never publishes (``aktywna: false`` in the model)
  is left out of the maximum for every company - the report names it.  This
  is fixed in the model, not inferred from the run, so a company's % does
  not change with the list it is scored on;
* must-have rules are pass/fail.
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
    # False = the data source never publishes this reading; the rule is left
    # out of the maximum for every company, so a score does not depend on
    # which other companies happen to be on the list.
    aktywna: bool = True
    uwaga: str = ""

    def points(self, value) -> float | None:
        """Points for ``value``; ``None`` when the reading is missing.

        Must-have rules are pass/fail: the full point or nothing.  A linear
        ramp between e.g. 0,50 and 0,51 USD EPS would hand out fractions for
        a condition that is either met or not.
        """
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        value = float(value)
        ascending = self.best >= self.worst
        if self.must_have:
            if self.inclusive_worst:
                passes = value >= self.worst if ascending else value <= self.worst
            else:
                passes = value > self.worst if ascending else value < self.worst
            return float(self.max) if passes else 0.0
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
    # Trela's loose screener in front of the model: rule id -> minimum reading.
    prefilter: dict = field(default_factory=dict)

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
        prefilter={k: float(v) for k, v in (data.get("prefiltr") or {}).items()},
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
    humanoid: bool = False                           # in the user's humanoid-robotics list

    @property
    def pct(self) -> float:
        return self.total / self.max_total if self.max_total else 0.0

    @property
    def flagged(self) -> bool:
        return bool(self.flags)

    @property
    def no_data(self) -> bool:
        """Most rules unreadable: a fetch failure, not a weak company."""
        return len(self.missing) * 2 > len(self.points)

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
    """Score every company; returns ``(ranked scores, rules left out of the maximum)``.

    Ranking: unflagged companies by total (Scrab formula), then flagged ones,
    also by total - a flag sends a company to the end of the list; companies
    whose data could not be read come last of all, so a fetch failure never
    looks better than a real flag.
    """
    years_since_ipo = years_since_ipo or {}
    dropped = [r for r in model.rules if not r.aktywna]
    active = {r.id for r in model.rules if r.aktywna}

    scores = [
        score_company(t, readings, model, active, years_since_ipo.get(t))
        for t, readings in readings_by_ticker.items()
    ]
    scores.sort(key=lambda s: (s.no_data, s.flagged, -s.pct, s.ticker))
    return scores, dropped


def _missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))
