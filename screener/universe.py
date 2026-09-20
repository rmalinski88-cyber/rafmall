"""Loading and validating the screened universe."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["ticker", "name"]
OPTIONAL_COLUMNS = ["market", "segment", "confidence", "notes"]


def load_universe(path: str | Path) -> pd.DataFrame:
    """Read the universe CSV, normalised and de-duplicated.

    Only ``ticker`` and ``name`` are required; the descriptive columns are
    filled with empty strings when absent so the rest of the pipeline can rely
    on them existing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"universe file not found: {path}")

    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    frame.columns = [c.strip().lower() for c in frame.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"universe file {path} is missing column(s): {', '.join(missing)}")

    for column in OPTIONAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""

    frame["ticker"] = frame["ticker"].str.strip()
    frame = frame[frame["ticker"] != ""]
    for column in ["name", *OPTIONAL_COLUMNS]:
        frame[column] = frame[column].fillna("").astype(str).str.strip()

    # A duplicated ticker would be scored twice and skew every percentile rank.
    frame = frame.drop_duplicates(subset="ticker", keep="first")

    return frame.reset_index(drop=True)[["ticker", "name", *OPTIONAL_COLUMNS]]
