"""On-disk cache for provider responses.

Free data sources rate-limit aggressively, and a screen over ~40 tickers
re-run a few times in an afternoon will get throttled without this.  Entries
are plain CSV/JSON on disk so they can be inspected or deleted by hand.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pandas as pd

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(key: str) -> str:
    return _SAFE.sub("_", key)


class Cache:
    """TTL cache keyed by ``(namespace, key)``."""

    def __init__(self, root: str | Path, ttl_hours: float, enabled: bool = True):
        self.root = Path(root)
        self.ttl_seconds = float(ttl_hours) * 3600.0
        self.enabled = enabled

    def _path(self, namespace: str, key: str, suffix: str) -> Path:
        return self.root / namespace / f"{_slug(key)}{suffix}"

    def _fresh(self, path: Path) -> bool:
        if not self.enabled or not path.exists():
            return False
        if self.ttl_seconds <= 0:
            return False
        return (time.time() - path.stat().st_mtime) < self.ttl_seconds

    # -- dataframes ----------------------------------------------------

    def get_frame(self, namespace: str, key: str) -> pd.DataFrame | None:
        path = self._path(namespace, key, ".csv")
        if not self._fresh(path):
            return None
        try:
            frame = pd.read_csv(path, index_col=0, parse_dates=True)
        except Exception:
            # A truncated or corrupt entry is a cache miss, never a crash.
            return None
        return frame

    def put_frame(self, namespace: str, key: str, frame: pd.DataFrame) -> None:
        if not self.enabled:
            return
        path = self._path(namespace, key, ".csv")
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path)

    # -- json ----------------------------------------------------------

    def get_json(self, namespace: str, key: str):
        path = self._path(namespace, key, ".json")
        if not self._fresh(path):
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def put_json(self, namespace: str, key: str, payload) -> None:
        if not self.enabled:
            return
        path = self._path(namespace, key, ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
