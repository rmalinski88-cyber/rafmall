"""Remembering which trades a scan has already reported.

An hourly routine should only speak up about what is new.  The state file is
a small JSON list of trade keys; deleting it simply makes the next scan treat
everything in the window as new.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Trade

MAX_KEYS = 20_000


class SeenStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.keys: set[str] = set()
        if self.path.exists():
            try:
                self.keys = set(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                self.keys = set()  # a corrupt file is a fresh start, not a crash

    def new(self, trades: list[Trade]) -> list[Trade]:
        return [t for t in trades if t.key not in self.keys]

    def remember(self, trades: list[Trade]) -> None:
        self.keys.update(t.key for t in trades)

    def is_new_key(self, key: str) -> bool:
        return key not in self.keys

    def remember_key(self, key: str) -> None:
        self.keys.add(key)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        keys = sorted(self.keys)[-MAX_KEYS:]
        self.path.write_text(json.dumps(keys), encoding="utf-8")
