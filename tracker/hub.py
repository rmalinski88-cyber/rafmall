"""The online tool: one hub page + data files, rebuilt by GitHub Actions.

Three jobs, mirroring what the user asked for:

* **Szukaj** - every instrument the lists know (stocks, ETFs, crypto) with a
  quote card, searchable in the browser from one JSON file.
* **Okazje** - today's anomalies (``tracker alerts``) and market setups
  (``tracker market``).
* **Inwestorzy** - fund/Congress/insider signals from ``tracker scan`` and
  the "Portfel Trumpa" bucket.

Everything is static: the generator reads the JSON the other commands wrote
into ``out/`` during the same run and renders HTML plus ``api/*.json`` for
the rafmall.ch front-end to consume later.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from screener.report import format as fmt
from screener.report.charts import sparkline

from .instruments import describe
from .lists import load_symbols

TEMPLATE_DIR = Path(__file__).parent

# (file, group label shown on the card, group key)
SOURCES = [
    ("data/universe_humanoid_global.csv", "Robotyka", "robotyka"),
    ("data/universe_surowce.csv", "Surowce", "surowce"),
    ("data/universe_infrastruktura.csv", "Energia", "energia"),
    ("data/universe_inne.csv", "Inne tematy", "inne"),
    ("data/etf.csv", "ETF", "etf"),
    ("data/crypto.csv", "Krypto", "krypto"),
    ("data/okazje.csv", "Okazje zakupowe", "okazje"),
    ("data/watchlist.csv", "Obserwowane", "obserwowane"),
    ("data/trump.csv", "Portfel Trumpa", "trump"),
]


def collect_instruments(provider, config: dict, sources=SOURCES, limit: int | None = None,
                        progress=None) -> list[dict]:
    """One quote card per distinct symbol, tagged with every list it sits on."""
    rows: dict[str, dict] = {}
    for path, label, key in sources:
        for entry in load_symbols(path):
            t = entry["ticker"]
            row = rows.setdefault(t, {"symbol": t, "name": entry.get("name") or t, "groups": [], "keys": [],
                                      "segment": entry.get("segment") or entry.get("group") or "",
                                      "market": entry.get("market") or "", "notes": entry.get("notes") or entry.get("note") or ""})
            if label not in row["groups"]:
                row["groups"].append(label)
                row["keys"].append(key)
            if not row["name"] or row["name"] == t:
                row["name"] = entry.get("name") or row["name"]
    symbols = list(rows.values())[:limit] if limit else list(rows.values())

    out = []
    for i, row in enumerate(symbols, 1):
        if progress:
            progress(i, len(symbols), row["symbol"])
        try:
            card = describe(row["symbol"], provider, config)
        except Exception as exc:
            card = {"symbol": row["symbol"], "error": str(exc)}
        closes = card.get("closes")
        spark = closes.tail(120) if closes is not None else None
        out.append({
            **{k: v for k, v in row.items()},
            "name": card.get("name") if not card.get("error") and card.get("name") not in (None, row["symbol"]) else row["name"],
            "asset_class": card.get("asset_class", ""),
            "error": card.get("error"),
            "last": card.get("last_close"), "currency": card.get("currency") or "",
            "market_cap": card.get("market_cap"), "total_assets": card.get("total_assets"),
            "ret_1m": card.get("ret_1m"), "ret_3m": card.get("ret_3m"), "ret_6m": card.get("ret_6m"), "ret_12m": card.get("ret_12m"),
            "rsi": card.get("rsi14"), "sma200": card.get("px_vs_sma200"), "sma50": card.get("px_vs_sma50"),
            "dist_high": card.get("dist_52w_high"), "trend": card.get("trend", ""),
            "atr": card.get("atr_pct"), "pe": card.get("trailing_pe"), "rev_growth": card.get("revenue_growth"),
            "spark": [round(float(v), 6) for v in spark.dropna().tolist()] if spark is not None else [],
        })
    return out


def latest_json(out_dir: Path, prefix: str) -> dict | None:
    files = sorted(out_dir.glob(f"{prefix}_*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def build_hub(instruments: list[dict], out_dir: Path, site_dir: Path, config: dict,
              base_url: str = "") -> list[Path]:
    """Render index.html + okazje.html and write api/*.json. Returns written paths."""
    site_dir.mkdir(parents=True, exist_ok=True)
    api = site_dir / "api"
    api.mkdir(exist_ok=True)
    today = date.today().isoformat()

    alerts = latest_json(out_dir, "alerts") or {"alerts": [], "checked": 0}
    market = latest_json(out_dir, "market") or {"setups": [], "checked": 0}
    signals = latest_json(out_dir, "signals") or {"signals": [], "new_trades": []}

    # Data for the front-end (rafmall.ch can fetch these directly).
    slim = [{k: v for k, v in r.items() if k not in ("notes",)} for r in instruments]
    written = []
    for name, payload in (("instruments", {"generated": today, "count": len(slim), "items": slim}),
                          ("alerts", alerts), ("market", market), ("signals", signals),
                          ("meta", {"generated": today, "instruments": len(slim), "alerts": len(alerts.get("alerts", [])),
                                    "setups": len(market.get("setups", [])), "signals": len(signals.get("signals", []))})):
        path = api / f"{name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
        written.append(path)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html"]))
    ctx = _context(instruments, alerts, market, signals, today, base_url)
    for template, target in (("hub_index.html", "index.html"), ("hub_okazje.html", "okazje.html"),
                             ("hub_szukaj.html", "szukaj.html")):
        html = env.get_template(template).render(**ctx)
        path = site_dir / target
        path.write_text(html, encoding="utf-8")
        written.append(path)

    # The tracker's own report becomes the investors page when the run produced one.
    reports = sorted(out_dir.glob("tracker_*.html"))
    if reports:
        (site_dir / "inwestorzy.html").write_text(reports[-1].read_text(encoding="utf-8"), encoding="utf-8")
        written.append(site_dir / "inwestorzy.html")
    return written


def _pct(v, signed=True):
    return fmt.pct(v, signed=signed)


def _context(instruments, alerts, market, signals, today, base_url) -> dict:
    by_symbol = {r["symbol"]: r for r in instruments}

    def row_view(r: dict) -> dict:
        import pandas as pd
        spark = pd.Series(r["spark"]) if r.get("spark") else None
        return {
            **r,
            "last_f": fmt.num(r.get("last"), 2) if r.get("last") is not None else fmt.DASH,
            "size_f": fmt.usd(r.get("total_assets") or r.get("market_cap")),
            "r1": _pct(r.get("ret_1m")), "r3": _pct(r.get("ret_3m")), "r12": _pct(r.get("ret_12m")),
            "rsi_f": fmt.num(r.get("rsi"), 0), "s200": _pct(r.get("sma200")), "dh": _pct(r.get("dist_high")),
            "tone1": _tone(r.get("ret_1m")), "tone12": _tone(r.get("ret_12m")),
            "spark_svg": Markup(sparkline(spark, width=110, height=28)) if spark is not None and len(spark) > 2 else "",
            "search": " ".join([r["symbol"], r.get("name") or "", r.get("notes") or "", r.get("market") or "",
                                r.get("segment") or "", " ".join(r.get("groups", []))]).lower(),
        }

    views = [row_view(r) for r in instruments]
    good = [v for v in views if not v.get("error")]
    classes = {"akcja": "Akcje", "ETF": "ETF", "krypto": "Krypto"}

    alert_rows = alerts.get("alerts", [])
    kinds = {}
    for a in alert_rows:
        kinds.setdefault(a.get("kind", "?"), []).append(a)
    kind_order = ["konfluencja", "okazja", "wolumen", "ruch", "wybicie", "poziom", "trend", "smart money"]
    alert_groups = [{"kind": k, "label": KIND_LABELS.get(k, k), "icon": KIND_ICONS.get(k, "•"), "items": kinds[k]}
                    for k in kind_order if k in kinds] + [
                   {"kind": k, "label": k, "icon": "•", "items": v} for k, v in kinds.items() if k not in kind_order]
    for g in alert_groups:
        for a in g["items"]:
            a["name"] = (by_symbol.get(a["ticker"]) or {}).get("name") or a.get("name") or a["ticker"]

    setups = market.get("setups", [])
    for s in setups:
        s["last_f"] = fmt.num(s.get("last_close"), 4 if (s.get("last_close") or 1) < 1 else 2)
        s["turnover_f"] = fmt.usd(s.get("avg_dollar_volume"))

    sig = signals.get("signals", [])
    top_signals = [s for s in sig if abs(s.get("score", 0)) >= 1][:25]
    for s in top_signals:
        s["tone"] = "good" if s["score"] >= 1 else "bad"
        s["name"] = (by_symbol.get(s["ticker"]) or {}).get("name") or s["ticker"]

    trump = [v for v in views if "trump" in v.get("keys", [])]
    movers_up = sorted(good, key=lambda v: -(v.get("ret_1m") or -9))[:8]
    movers_down = sorted(good, key=lambda v: (v.get("ret_1m") or 9))[:8]
    konfluencje = kinds.get("konfluencja", [])

    return {
        "today": today, "base_url": base_url,
        "instruments": views, "n_instruments": len(good), "n_errors": len(views) - len(good),
        "classes": classes,
        "groups": [lbl for _, lbl, _ in SOURCES],
        "alert_groups": alert_groups, "n_alerts": len(alert_rows), "checked": alerts.get("checked", 0),
        "setups": setups, "n_setups": len(setups), "market_checked": market.get("checked", 0),
        "top_signals": top_signals, "n_signals": len(sig), "new_trades": signals.get("new_trades", [])[:30],
        "trump": trump, "movers_up": movers_up, "movers_down": movers_down, "konfluencje": konfluencje,
        "warnings": (alerts.get("warnings") or [])[:8],
        "dash": fmt.DASH,
    }


def _tone(v):
    if v is None:
        return "neutral"
    return "good" if v > 0 else "bad" if v < 0 else "neutral"


KIND_LABELS = {"konfluencja": "Konfluencja — kilka sygnałów naraz", "okazja": "Okazje zakupowe (Twoje progi)",
               "wolumen": "Skok wolumenu", "ruch": "Duży ruch ceny", "wybicie": "Szczyt / dołek 52 tygodni",
               "poziom": "Przebicie poziomu", "trend": "Przecięcie SMA200", "smart money": "Insiderzy i Kongres"}
KIND_ICONS = {"konfluencja": "🔥", "okazja": "🟢", "wolumen": "📊", "ruch": "⚡", "wybicie": "🚀",
              "poziom": "🔑", "trend": "📈", "smart money": "🕵️"}
