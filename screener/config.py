"""Configuration loading and defaults."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path("config/default.yml")


def load_config(path: str | Path | None = None) -> dict:
    """Load a YAML config, falling back to the bundled default."""
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError(f"config file must contain a mapping: {path}")
    return config


def resolve_profile(config: dict, name: str | None = None) -> tuple[str, dict]:
    """Return ``(profile_name, profile_block)``, validated."""
    profiles = config.get("profiles") or {}
    chosen = name or config.get("profile") or "balanced"
    if chosen not in profiles:
        available = ", ".join(sorted(profiles)) or "(none)"
        raise KeyError(f"unknown scoring profile {chosen!r}; available: {available}")
    return chosen, copy.deepcopy(profiles[chosen])


def group_weights(profile: dict) -> dict:
    """Fundamental/technical blend for a profile, defaulting to an even split."""
    weights = profile.get("group_weights") or {}
    return {
        "fundamental": float(weights.get("fundamental", 0.5)),
        "technical": float(weights.get("technical", 0.5)),
    }


def benchmark_for(ticker: str, config: dict) -> str | None:
    """Index symbol used for this ticker's relative strength."""
    mapping = config.get("benchmarks") or {}
    upper = ticker.upper()
    # Longest suffix first so ".TWO" wins over ".TW".
    for suffix in sorted(mapping, key=len, reverse=True):
        if upper.endswith(suffix.upper()):
            return mapping[suffix]
    return mapping.get("default")
