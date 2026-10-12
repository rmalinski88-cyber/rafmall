#!/usr/bin/env python3
"""Pierwsze uruchomienie na komputerze: wszystko po kolei, jeden log do wysłania.

    python scripts/first_run.py            # pełny przebieg (20-40 min, zależnie od Yahoo)
    python scripts/first_run.py --quick    # bez strony i skanu rynku (kilka minut)

Każdy krok ma nagłówek i kod wyjścia; błąd jednego kroku nie zatrzymuje
reszty. Wynik trafia na ekran i do out/first_run_<data>.log.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

UNIVERSES = [
    "data/universe_humanoid_global.csv",
    "data/universe_surowce.csv",
    "data/universe_infrastruktura.csv",
    "data/universe_inne.csv",
    "data/etf.csv",
    "data/okazje.csv",
    "data/crypto.csv",
]

SITE = [PY, "-m", "screener", "--universe", "data/universe_humanoid_global.csv", "site",
        "--out", "out/site/roboty.html",
        "--extra", "Surowce=data/universe_surowce.csv",
        "--extra", "Energia=data/universe_infrastruktura.csv",
        "--extra", "Inne tematy=data/universe_inne.csv"]


def steps(quick: bool) -> list[tuple[str, list[str]]]:
    out = [
        ("Testy offline (powinny przejść zawsze)", [PY, "-m", "pytest", "tests", "-q"]),
        ("Konfiguracja i dostęp do źródeł", [PY, "-m", "tracker", "check"]),
    ]
    out += [(f"Weryfikacja tickerów: {u}", [PY, "-m", "screener", "--universe", u, "validate"]) for u in UNIVERSES]
    out += [
        ("Test akceptacyjny reguły: ARB-USD, oczekiwany sygnał ok. 2026-08-26/27",
         [PY, "-m", "tracker", "replay", "ARB-USD", "--rule", "pullback", "--days", "120"]),
        ("Ta sama reguła na NVDA (kontrola: nie powinna strzelać codziennie)",
         [PY, "-m", "tracker", "replay", "NVDA", "--rule", "pullback", "--days", "120"]),
        ("Alerty na listach (wszystkie bieżące)", [PY, "-m", "tracker", "alerts", "--all"]),
        ("Tracker: Kongres / insiderzy / 13F / sygnały", [PY, "-m", "tracker", "scan", "--no-quotes"]),
    ]
    if not quick:
        out += [
            ("Skan rynku (ograniczony do 150 symboli)", [PY, "-m", "tracker", "market", "--all", "--limit", "150"]),
            ("Strona WWW: out/site/roboty.html", SITE),
        ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    (ROOT / "out").mkdir(exist_ok=True)
    log_path = ROOT / "out" / f"first_run_{date.today().isoformat()}.log"
    failures = []
    with log_path.open("w", encoding="utf-8") as log:
        def emit(text: str) -> None:
            print(text, flush=True)
            log.write(text + "\n")
            log.flush()

        emit(f"# Pierwsze uruchomienie · {date.today()} · {sys.platform} · Python {sys.version.split()[0]}")
        for i, (title, cmd) in enumerate(steps(args.quick), 1):
            emit(f"\n{'=' * 78}\n## {i}. {title}\n$ {' '.join(cmd[1:])}\n{'=' * 78}")
            started = time.time()
            proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace")
            emit(proc.stdout.rstrip())
            if proc.stderr.strip():
                emit("[stderr]\n" + proc.stderr.rstrip())
            status = "OK" if proc.returncode == 0 else f"BŁĄD (kod {proc.returncode})"
            emit(f"-- {status} · {time.time() - started:.0f} s")
            if proc.returncode != 0:
                failures.append(title)

        emit(f"\n{'=' * 78}\n## Podsumowanie")
        emit("Wszystkie kroki OK." if not failures else "Kroki z błędem:\n" + "\n".join(f"  - {f}" for f in failures))
        emit(f"\nLog: {log_path}\nWyślij ten plik Claude'owi — od niego zaczyna się poprawianie.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
