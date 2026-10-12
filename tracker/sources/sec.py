"""SEC EDGAR: insider trades (Form 4) and fund holdings (13F-HR).

Free and keyless, but the SEC requires a ``User-Agent`` that identifies you
(name and e-mail) and allows at most 10 requests per second.  Archived filings
never change, so they are cached for a long time; the submission indexes that
list new filings are cached briefly so an hourly scan sees fresh data.

The XML parsers are module-level functions so they can be tested on literal
documents without any network.
"""

from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date

from ..models import BUY, SELL, Holding, Trade

WWW = "https://www.sec.gov"
DATA = "https://data.sec.gov"

# Only open-market purchases and sales say anything about conviction.  Grants
# (A), option exercises (M), tax withholding (F) and gifts (G) are mechanical.
_CODE_SIDE = {"P": BUY, "S": SELL}

_CSUITE = re.compile(r"\b(CEO|CFO|COO|CTO|PRESIDENT|CHIEF|CHAIR)", re.IGNORECASE)


class SecClient:
    def __init__(self, user_agent: str, fresh_cache=None, archive_cache=None, throttle: float = 0.15):
        if not user_agent or "@" not in user_agent:
            from .base import FeedError

            raise FeedError(
                "SEC wymaga nagłówka User-Agent z imieniem i adresem e-mail. "
                "Ustaw zmienną SEC_USER_AGENT, np.: export SEC_USER_AGENT=\"Jan Kowalski jan@example.com\""
            )
        self.user_agent = user_agent
        self.fresh_cache = fresh_cache
        self.archive_cache = archive_cache
        self.throttle = throttle
        self._last_request = 0.0
        self._tickers: dict[str, tuple[int, str]] | None = None

    # -- transport -----------------------------------------------------

    def _get(self, url: str, archive: bool = False) -> str:
        cache = self.archive_cache if archive else self.fresh_cache
        if cache is not None:
            hit = cache.get_json("sec", url)
            if hit is not None:
                return hit["text"]

        import requests

        wait = self.throttle - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        response = requests.get(
            url,
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
            timeout=30,
        )
        self._last_request = time.monotonic()
        response.raise_for_status()
        text = response.text
        if cache is not None:
            cache.put_json("sec", url, {"text": text})
        return text

    # -- lookups -------------------------------------------------------

    def tickers(self) -> dict[str, tuple[int, str]]:
        """``TICKER -> (cik, company name)`` for every SEC registrant."""
        if self._tickers is None:
            payload = json.loads(self._get(f"{WWW}/files/company_tickers.json", archive=False))
            self._tickers = parse_ticker_map(payload)
        return self._tickers

    def cik_for(self, ticker: str) -> int | None:
        entry = self.tickers().get(ticker.upper().replace(".", "-"))
        return entry[0] if entry else None

    def filings(self, cik: int, forms: set[str], since: date | None = None, limit: int = 50) -> list[dict]:
        """Most recent filings of the given form types, newest first."""
        payload = json.loads(self._get(f"{DATA}/submissions/CIK{cik:010d}.json"))
        return select_filings(payload, forms, since, limit)

    def document(self, cik: int, accession: str, name: str) -> str:
        folder = accession.replace("-", "")
        return self._get(f"{WWW}/Archives/edgar/data/{cik}/{folder}/{name}", archive=True)

    def filing_index(self, cik: int, accession: str) -> list[str]:
        folder = accession.replace("-", "")
        payload = json.loads(
            self._get(f"{WWW}/Archives/edgar/data/{cik}/{folder}/index.json", archive=True)
        )
        return [item["name"] for item in payload.get("directory", {}).get("item", [])]

    # -- insiders ------------------------------------------------------

    def insider_trades(self, ticker: str, since: date, max_filings: int = 40) -> list[Trade]:
        cik = self.cik_for(ticker)
        if cik is None:
            return []
        trades: list[Trade] = []
        for filing in self.filings(cik, {"4"}, since=since, limit=max_filings):
            # primaryDocument points at the XSL-rendered HTML view
            # ("xslF345X05/form4.xml"); the raw XML has the same file name.
            raw_name = filing["primary"].split("/")[-1]
            try:
                xml_text = self.document(cik, filing["accession"], raw_name)
            except Exception:
                continue
            trades.extend(parse_form4(xml_text, filed=filing["filed"], ticker_hint=ticker))
        return trades

    # -- 13F -----------------------------------------------------------

    def latest_13f(self, cik: int, count: int = 2) -> list[tuple[dict, list[Holding]]]:
        """The ``count`` most recent original 13F-HR filings with their holdings."""
        out = []
        for filing in self.filings(cik, {"13F-HR"}, limit=count):
            names = self.filing_index(cik, filing["accession"])
            holdings: list[Holding] = []
            for name in names:
                if not name.lower().endswith(".xml") or name.lower() == "primary_doc.xml":
                    continue
                holdings = parse_info_table(self.document(cik, filing["accession"], name),
                                            filed=filing["filed"])
                if holdings:
                    break
            out.append((filing, holdings))
        return out


# -- pure parsers ------------------------------------------------------------


def parse_ticker_map(payload: dict) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}
    rows = payload.values() if isinstance(payload, dict) else payload
    for row in rows:
        ticker = str(row.get("ticker", "")).upper()
        if ticker and ticker not in out:  # first entry is the primary listing
            out[ticker] = (int(row["cik_str"]), str(row.get("title", "")))
    return out


def select_filings(payload: dict, forms: set[str], since: date | None, limit: int) -> list[dict]:
    recent = payload.get("filings", {}).get("recent", {})
    out = []
    for i, form in enumerate(recent.get("form", [])):
        if form not in forms:
            continue
        filed = _date(recent["filingDate"][i])
        if since is not None and filed is not None and filed < since:
            continue
        out.append({
            "form": form,
            "accession": recent["accessionNumber"][i],
            "filed": filed,
            "period": _date((recent.get("reportDate") or [None] * (i + 1))[i]),
            "primary": recent["primaryDocument"][i],
        })
        if len(out) >= limit:
            break
    return out


def parse_form4(xml_text: str, filed: date | None = None, ticker_hint: str = "") -> list[Trade]:
    """Open-market purchases and sales from one Form 4 document."""
    try:
        root = _strip_namespaces(ET.fromstring(xml_text.encode("utf-8")))
    except ET.ParseError:
        return []

    ticker = (_text(root, "issuer/issuerTradingSymbol") or ticker_hint).upper()
    owners = root.findall("reportingOwner")
    names = [_text(o, "reportingOwnerId/rptOwnerName") for o in owners]
    actor = " / ".join(n for n in names if n) or "?"
    role = _role(owners[0].find("reportingOwnerRelationship")) if owners else ""
    # Newer Form 4s (2023+) carry an explicit 10b5-1 checkbox.
    planned = (_text(root, "aff10b5One") or "").strip().lower() in ("1", "true")

    trades = []
    for row in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        side = _CODE_SIDE.get((_text(row, "transactionCoding/transactionCode") or "").strip())
        if side is None:
            continue
        shares = _float(_text(row, "transactionAmounts/transactionShares/value"))
        price = _float(_text(row, "transactionAmounts/transactionPricePerShare/value"))
        value = shares * price if shares is not None and price is not None else None
        trades.append(Trade(
            source="insider",
            actor=actor,
            role=role,
            ticker=ticker,
            side=side,
            traded=_date(_text(row, "transactionDate/value")),
            reported=filed,
            amount_low=value,
            amount_high=value,
            shares=shares,
            price=price,
            planned=planned and side == SELL,
            detail=_text(row, "securityTitle/value") or "",
        ))
    return trades


def parse_info_table(xml_text: str, filed: date | None = None) -> list[Holding]:
    """13F information table, aggregated by ``(CUSIP, put/call)``."""
    try:
        root = _strip_namespaces(ET.fromstring(xml_text.encode("utf-8")))
    except ET.ParseError:
        return []

    # Filings before 2023 reported value in thousands of dollars.
    multiplier = 1000.0 if filed is not None and filed < date(2023, 1, 3) else 1.0

    merged: dict[tuple[str, str], dict] = {}
    for row in root.iter("infoTable"):
        cusip = (_text(row, "cusip") or "").upper()
        put_call = (_text(row, "putCall") or "").upper()
        if not cusip:
            continue
        slot = merged.setdefault((cusip, put_call), {
            "issuer": _text(row, "nameOfIssuer") or cusip, "value": 0.0, "shares": 0.0,
        })
        slot["value"] += (_float(_text(row, "value")) or 0.0) * multiplier
        slot["shares"] += _float(_text(row, "shrsOrPrnAmt/sshPrnamt")) or 0.0

    return [
        Holding(issuer=v["issuer"], cusip=c, value=v["value"], shares=v["shares"], put_call=pc)
        for (c, pc), v in merged.items()
    ]


def is_csuite(role: str) -> bool:
    return bool(_CSUITE.search(role or ""))


def _role(rel) -> str:
    if rel is None:
        return ""
    parts = []
    title = _text(rel, "officerTitle")
    if title:
        parts.append(title.strip())
    elif _flag(_text(rel, "isOfficer")):
        parts.append("Officer")
    if _flag(_text(rel, "isDirector")):
        parts.append("Director")
    if _flag(_text(rel, "isTenPercentOwner")):
        parts.append("10% owner")
    return ", ".join(parts)


def _strip_namespaces(root):
    for element in root.iter():
        if isinstance(element.tag, str) and "}" in element.tag:
            element.tag = element.tag.split("}", 1)[1]
    return root


def _text(node, path: str) -> str | None:
    found = node.find(path)
    if found is None or found.text is None:
        return None
    return found.text.strip()


def _flag(value) -> bool:
    return (value or "").strip().lower() in ("1", "true")


def _float(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None
