"""Cross-sectional scoring.

Every metric is converted to a **percentile rank within the screened universe**
rather than compared against an absolute threshold.  That choice matters:
absolute cut-offs ("P/E under 20") are meaningless across Tokyo, Seoul, Taipei
and Shenzhen at once, and meaningless across a profitable component maker and a
pre-revenue humanoid developer.  A rank answers the only question a screener
can honestly answer - *how does this name compare with its peers in this
basket, today*.

Consequences worth knowing before reading the output:

* Scores are relative.  A 90 in a weak universe is still a weak company.
* Change the universe and every score changes.
* A metric is only ranked when at least ``MIN_RANKABLE`` companies report it;
  ranking two companies against each other produces 100 and 0, which is noise.
* Missing data is never imputed.  Weights are renormalised over the metrics a
  company actually reports, and the resulting coverage is published alongside
  the score so a high score built on three of eleven metrics is visible as such.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

#: Fewer reporters than this and a metric is dropped rather than ranked.
MIN_RANKABLE = 3

GROUPS = ("fundamental", "technical")

#: Display names (Polish) for everything that can end up in a report.
LABELS = {
    # fundamental
    "market_cap": "Kapitalizacja",
    "market_cap_usd": "Kapitalizacja (USD)",
    "revenue_growth": "Wzrost przychodów",
    "earnings_growth": "Wzrost zysku",
    "gross_margin": "Marża brutto",
    "operating_margin": "Marża operacyjna",
    "profit_margin": "Marża netto",
    "return_on_equity": "ROE",
    "return_on_assets": "ROA",
    "fcf_margin": "Marża FCF",
    "debt_to_equity": "Dług / kapitał",
    "current_ratio": "Wskaźnik płynności",
    "net_cash_to_mcap": "Gotówka netto / kap.",
    "earnings_yield": "Rentowność zysku (E/P)",
    "price_to_sales": "Cena / przychody",
    "price_to_book": "Cena / wartość księgowa",
    "ev_to_ebitda": "EV / EBITDA",
    "peg_ratio": "PEG",
    "trailing_pe": "C/Z",
    "forward_pe": "C/Z prognoz.",
    # technical
    "px_vs_sma50": "Cena vs SMA50",
    "px_vs_sma200": "Cena vs SMA200",
    "sma50_vs_sma200": "SMA50 vs SMA200",
    "rsi14": "RSI(14)",
    "macd_hist_pct": "Histogram MACD",
    "ret_1m": "Stopa zwrotu 1M",
    "ret_3m": "Stopa zwrotu 3M",
    "ret_6m": "Stopa zwrotu 6M",
    "ret_12m": "Stopa zwrotu 12M",
    "rs_3m": "Siła względna 3M",
    "rs_6m": "Siła względna 6M",
    "dist_52w_high": "Dystans do szczytu 52T",
    "pos_52w_range": "Pozycja w zakresie 52T",
    "volume_trend": "Trend wolumenu",
    "atr_pct": "ATR %",
    "max_drawdown_12m": "Max obsunięcie 12M",
}


@dataclass(frozen=True)
class MetricSpec:
    key: str
    group: str
    weight: float
    higher_is_better: bool

    @property
    def label(self) -> str:
        return LABELS.get(self.key, self.key)


def build_specs(profile: dict) -> list[MetricSpec]:
    """Turn a profile block from the config into metric specs.

    Expected shape::

        fundamental:
          revenue_growth: {weight: 3.0, direction: high}
        technical:
          rsi14: {weight: 1.0, direction: high}
    """
    specs: list[MetricSpec] = []
    for group in GROUPS:
        for key, cfg in (profile.get(group) or {}).items():
            if isinstance(cfg, (int, float)):
                weight, direction = float(cfg), "high"
            else:
                weight = float(cfg.get("weight", 1.0))
                direction = str(cfg.get("direction", "high")).lower()
            if direction not in ("high", "low"):
                raise ValueError(
                    f"metric '{key}': direction must be 'high' or 'low', got {direction!r}"
                )
            if weight <= 0:
                continue
            specs.append(
                MetricSpec(key=key, group=group, weight=weight, higher_is_better=direction == "high")
            )
    if not specs:
        raise ValueError("scoring profile defines no metrics with a positive weight")
    return specs


def percentile_rank(series: pd.Series, higher_is_better: bool) -> pd.Series:
    """Rank to 0-100, ``NaN`` preserved, ``NaN`` everywhere if too few reporters."""
    values = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if values.notna().sum() < MIN_RANKABLE:
        return pd.Series(np.nan, index=series.index, dtype=float)
    # average ties so a cluster of identical values shares one rank
    return values.rank(pct=True, ascending=higher_is_better, method="average") * 100.0


def score_universe(frame: pd.DataFrame, specs: list[MetricSpec], group_weights: dict) -> pd.DataFrame:
    """Add per-metric ranks, group scores, coverage and the composite score.

    Returns a new frame; the input is not modified.
    """
    result = frame.copy()

    ranks: dict[str, pd.Series] = {}
    usable: list[MetricSpec] = []
    for spec in specs:
        if spec.key not in result.columns:
            continue
        ranked = percentile_rank(result[spec.key], spec.higher_is_better)
        if ranked.notna().sum() == 0:
            continue
        ranks[spec.key] = ranked
        result[f"rank_{spec.key}"] = ranked
        usable.append(spec)

    for group in GROUPS:
        group_specs = [s for s in usable if s.group == group]
        score, coverage = _weighted_group_score(ranks, group_specs, result.index)
        result[f"{group}_score"] = score
        result[f"{group}_coverage"] = coverage

    result["composite_score"] = _composite(result, group_weights)
    return result


def _weighted_group_score(
    ranks: dict[str, pd.Series], specs: list[MetricSpec], index: pd.Index
) -> tuple[pd.Series, pd.Series]:
    """Weighted mean of available ranks, plus the share of weight available."""
    if not specs:
        nan = pd.Series(np.nan, index=index, dtype=float)
        return nan, pd.Series(0.0, index=index, dtype=float)

    total_weight = sum(s.weight for s in specs)
    weighted_sum = pd.Series(0.0, index=index, dtype=float)
    available_weight = pd.Series(0.0, index=index, dtype=float)

    for spec in specs:
        ranked = ranks[spec.key]
        present = ranked.notna()
        weighted_sum = weighted_sum.add(ranked.fillna(0.0) * spec.weight, fill_value=0.0)
        available_weight = available_weight.add(present.astype(float) * spec.weight, fill_value=0.0)

    score = weighted_sum / available_weight.replace(0.0, np.nan)
    return score, available_weight / total_weight


def _composite(frame: pd.DataFrame, group_weights: dict) -> pd.Series:
    """Blend the group scores, renormalising when one group is unavailable."""
    weighted_sum = pd.Series(0.0, index=frame.index, dtype=float)
    used_weight = pd.Series(0.0, index=frame.index, dtype=float)

    for group in GROUPS:
        weight = float(group_weights.get(group, 0.0))
        if weight <= 0:
            continue
        score = frame[f"{group}_score"]
        present = score.notna()
        weighted_sum = weighted_sum.add(score.fillna(0.0) * weight, fill_value=0.0)
        used_weight = used_weight.add(present.astype(float) * weight, fill_value=0.0)

    return weighted_sum / used_weight.replace(0.0, np.nan)
