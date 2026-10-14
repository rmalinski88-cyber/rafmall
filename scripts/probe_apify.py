"""Apify from GitHub Actions: find an actor for analyst price targets, then test it cheaply.

The cloud session cannot reach apify.com; Actions can.  Two modes:

    python scripts/probe_apify.py szukaj "price target"
        Free: searches the Apify Store and prints, for the best matches, the
        price model and the input schema - enough to choose an actor without
        spending credits.

    python scripts/probe_apify.py test "autor~aktor" '{"tickers": ["2330.TW"]}'
        Paid: one run of the actor with the given input, capped by
        MAX_ITEMS and MAX_CHARGE_USD, printing the first records as they come.

The key comes from the APIFY_TOKEN environment variable (a GitHub secret);
it is never printed.
"""

from __future__ import annotations

import json
import os
import sys

import requests

API = "https://api.apify.com/v2"
MAX_ITEMS = 20
MAX_CHARGE_USD = 0.50
TIMEOUT = 180


def _token() -> str:
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        sys.exit("Brak sekretu APIFY_TOKEN (GitHub → Settings → Secrets and variables → Actions).")
    return token


def _get(path: str, **params) -> dict:
    response = requests.get(f"{API}{path}", params=params,
                            headers={"Authorization": f"Bearer {_token()}"}, timeout=60)
    response.raise_for_status()
    return response.json().get("data", {})


def search(phrase: str, limit: int = 8) -> None:
    items = _get("/store", search=phrase, limit=limit).get("items", [])
    print(f"Apify Store: '{phrase}' — {len(items)} wyników\n")
    for item in items:
        actor_id = f"{item.get('username')}~{item.get('name')}"
        stats = item.get("stats") or {}
        print(f"=== {actor_id} — {item.get('title')}")
        print(f"    {(item.get('description') or '')[:300]}")
        print(f"    uruchomień: {stats.get('totalRuns')}, użytkowników: {stats.get('totalUsers')}")
        print(f"    cennik: {json.dumps(item.get('currentPricingInfo') or {}, ensure_ascii=False)[:300]}")
        try:
            build = _get(f"/acts/{actor_id}/builds/default")
        except requests.HTTPError as exc:
            print(f"    schemat wejścia: niedostępny ({exc.response.status_code})\n")
            continue
        schema = build.get("inputSchema") or (build.get("actorDefinition") or {}).get("input")
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except ValueError:
                schema = None
        props = (schema or {}).get("properties") or {}
        for name, spec in props.items():
            example = spec.get("prefill", spec.get("default", spec.get("example")))
            print(f"    wejście {name}: {spec.get('type')} — {(spec.get('title') or '')[:60]}"
                  + (f" (np. {json.dumps(example, ensure_ascii=False)[:80]})" if example is not None else ""))
        print()


def test(actor_id: str, raw_input: str) -> None:
    payload = json.loads(raw_input or "{}")
    headers = {"Authorization": f"Bearer {_token()}"}
    response = requests.post(
        f"{API}/acts/{actor_id}/runs",
        params={"waitForFinish": TIMEOUT, "maxItems": MAX_ITEMS, "maxTotalChargeUsd": MAX_CHARGE_USD},
        headers=headers, json=payload, timeout=TIMEOUT + 30,
    )
    print(f"{actor_id}: HTTP {response.status_code}, limit {MAX_ITEMS} rekordów / {MAX_CHARGE_USD} USD")
    if response.status_code >= 400:
        print(response.text[:2000])
        return
    run = response.json().get("data", {})
    usage = run.get("usageTotalUsd")
    print(f"przebieg {run.get('id')}: {run.get('status')}"
          + (f", koszt {usage:.4f} USD" if isinstance(usage, (int, float)) else ""))
    if run.get("status") != "SUCCEEDED":
        print("--- log aktora (koniec) ---")
        print(_run_log(run.get("id")))
    items = requests.get(f"{API}/datasets/{run.get('defaultDatasetId')}/items",
                         params={"limit": MAX_ITEMS, "clean": "true"}, headers=headers, timeout=60)
    try:
        rows = items.json()
    except ValueError:
        rows = []
    print(f"--- rekordy: {len(rows) if isinstance(rows, list) else '?'} ---")
    for item in (rows if isinstance(rows, list) else [])[:MAX_ITEMS]:
        print(json.dumps(item, ensure_ascii=False)[:3000])


def _run_log(run_id: str | None, lines: int = 60) -> str:
    if not run_id:
        return "(brak id przebiegu)"
    response = requests.get(f"{API}/actor-runs/{run_id}/log",
                            headers={"Authorization": f"Bearer {_token()}"}, timeout=60)
    return "\n".join(response.text.splitlines()[-lines:])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "szukaj"
    if mode == "szukaj":
        for phrase in (sys.argv[2:] or ["analyst price target", "price target history", "marketscreener"]):
            search(phrase)
    elif mode == "test" and len(sys.argv) >= 3:
        test(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "{}")
    else:
        sys.exit(__doc__)
