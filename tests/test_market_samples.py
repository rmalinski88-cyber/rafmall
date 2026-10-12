"""Acceptance tests on real bars kept in data/samples (see data/samples/README.md).

The pullback rule was written for one hand-picked example: Arbitrum, impulse
through EMA30 on 19 Aug 2026, correction, entry on 26 Aug 2026.  The scanner
has to find exactly that day.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"
ARB = SAMPLES / "ARB11841-USD.csv"


def _replay(symbol_file: Path, rule: str, start: date, end: date):
    from tracker.market import DEFAULTS, RULES

    frame = pd.read_csv(symbol_file, index_col=0)
    frame.index = pd.to_datetime(frame.index)
    hits = []
    for k in range(60, len(frame) + 1):
        day = frame.index[k - 1].date()
        if not start <= day <= end:
            continue
        hit = RULES[rule](symbol_file.stem, symbol_file.stem, frame.iloc[:k], DEFAULTS)
        if hit is not None:
            hits.append(hit)
    return hits


@pytest.mark.skipif(not ARB.exists(), reason="sample bars missing")
def test_arb_pullback_entry_is_26_aug_2026():
    hits = _replay(ARB, "pullback", date(2026, 8, 1), date(2026, 8, 31))
    assert [h.day for h in hits] == [date(2026, 8, 26)]
    assert hits[0].impulse_day == date(2026, 8, 19)
    assert hits[0].key == f"pullback|{ARB.stem}|2026-08-19"


@pytest.mark.skipif(not ARB.exists(), reason="sample bars missing")
def test_arb_ema30_hold_confirms_three_sessions_after_the_break():
    hits = _replay(ARB, "ema30", date(2026, 8, 1), date(2026, 9, 10))
    assert [h.day for h in hits] == [date(2026, 8, 21), date(2026, 9, 2)]


@pytest.mark.skipif(not ARB.exists(), reason="sample bars missing")
def test_samples_replay_command_dedupes_by_impulse(capsys):
    from tracker.cli import main

    assert main(["--provider", "samples", "--no-cache", "replay", "ARB11841-USD", "--rule", "pullback", "--days", "120"]) == 0
    out = capsys.readouterr().out
    assert "2026-08-26" in out and out.count("impuls 2026-07-09") == 1
    assert "alert idzie raz" in out
