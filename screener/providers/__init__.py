"""Provider registry.

Adding a paid source means writing one module with the ``DataProvider``
interface and adding one line here.
"""

from __future__ import annotations

from .base import DataProvider, ProviderError

_REGISTRY = {
    "tradingview": "screener.providers.tradingview:TradingViewProvider",
    "yahoo": "screener.providers.yahoo:YahooProvider",
    "fixture": "screener.providers.fixture:FixtureProvider",
    "samples": "screener.providers.samples:SamplesProvider",
}


def available_providers() -> list[str]:
    return sorted(_REGISTRY)


def get_provider(name: str, cache=None) -> DataProvider:
    """Instantiate a provider by short name."""
    key = (name or "").lower()
    if key not in _REGISTRY:
        raise ProviderError(
            f"unknown provider {name!r}; available: {', '.join(available_providers())}"
        )

    module_path, class_name = _REGISTRY[key].split(":")
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)(cache=cache)


__all__ = ["DataProvider", "ProviderError", "available_providers", "get_provider"]
