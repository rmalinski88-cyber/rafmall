"""13F holdings: comparing two filings and naming the issuers.

A 13F lists CUSIPs and issuer names, not tickers.  Tickers are resolved first
from a small hand-kept CUSIP table, then by matching the normalised issuer
name against SEC's company list.  Anything still unmatched keeps its issuer
name and simply has no ticker - it is never guessed.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import ADD, EXIT, HOLD, NEW, TRIM, Fund, FundChange, Holding

_NOISE = {
    "INC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "NEW",
    "DEL", "THE", "CL", "CLASS", "A", "B", "C", "COM", "SA", "NV", "AG", "SE",
    "LP", "LLC", "HLDGS", "HOLDINGS", "GROUP", "GRP", "ADR", "SPONSORED", "SHS",
}
_PUNCT = re.compile(r"[^A-Z0-9 ]+")


def load_funds(path: str | Path) -> list[Fund]:
    with Path(path).open(encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("key") and not r["key"].startswith("#")]
    return [Fund(key=r["key"].strip(), name=r["fund"].strip(), manager=r["manager"].strip(),
                 cik=int(r["cik"])) for r in rows]


def load_cusip_map(path: str | Path) -> dict[str, str]:
    path = Path(path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return {r["cusip"].strip().upper(): r["ticker"].strip().upper()
                for r in csv.DictReader(handle) if r.get("cusip")}


def normalise_name(name: str) -> str:
    words = _PUNCT.sub(" ", (name or "").upper()).split()
    return " ".join(w for w in words if w not in _NOISE)


def build_name_index(tickers: dict[str, tuple[int, str]]) -> dict[str, str]:
    """Normalised company name -> ticker; first (primary) listing wins."""
    index: dict[str, str] = {}
    for ticker, (_, title) in tickers.items():
        key = normalise_name(title)
        if key and key not in index:
            index[key] = ticker
    return index


def resolve_tickers(holdings: list[Holding], cusip_map: dict[str, str],
                    name_index: dict[str, str]) -> list[Holding]:
    out = []
    for h in holdings:
        ticker = h.ticker or cusip_map.get(h.cusip) or name_index.get(normalise_name(h.issuer))
        out.append(Holding(h.issuer, h.cusip, h.value, h.shares, h.put_call, ticker))
    return out


def diff_holdings(now: list[Holding], prev: list[Holding], min_change: float = 0.05) -> list[FundChange]:
    """Position-by-position change between two 13F filings.

    A share-count move smaller than ``min_change`` counts as unchanged, so
    rounding and small rebalancing do not read as conviction.
    """
    total = sum(h.value for h in now) or None
    before = {(h.cusip, h.put_call): h for h in prev}
    after = {(h.cusip, h.put_call): h for h in now}

    changes = []
    for key in after.keys() | before.keys():
        cur, old = after.get(key), before.get(key)
        ref = cur or old
        shares_now = cur.shares if cur else 0.0
        shares_prev = old.shares if old else 0.0

        if old is None or shares_prev == 0:
            kind = NEW
        elif cur is None or shares_now == 0:
            kind = EXIT
        else:
            move = shares_now / shares_prev - 1.0
            kind = ADD if move >= min_change else TRIM if move <= -min_change else HOLD

        changes.append(FundChange(
            issuer=ref.issuer,
            cusip=ref.cusip,
            ticker=(cur.ticker if cur else None) or (old.ticker if old else None),
            kind=kind,
            shares_now=shares_now,
            shares_prev=shares_prev,
            value_now=cur.value if cur else 0.0,
            value_prev=old.value if old else 0.0,
            weight_now=(cur.value / total) if (cur and total) else None,
            put_call=ref.put_call,
        ))

    changes.sort(key=lambda c: (c.value_now, c.value_prev), reverse=True)
    return changes
