"""Load KEY=VALUE pairs from a ``.env`` file into the environment.

Keeps secrets (SEC contact, Quiver key, Discord webhook, FTP login) out of
the config file and out of git, and spares Windows users the ``export``
dance.  Existing environment variables win over the file.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path = ".env") -> int:
    """Return how many variables were set."""
    path = Path(path)
    if not path.exists():
        return 0
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key.startswith("export "):
            key = key[7:].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
            count += 1
    return count
