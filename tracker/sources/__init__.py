"""Trade feeds: where congressional, insider and 13F data comes from.

``live`` reads SEC EDGAR (insiders, 13F; free) and Quiver Quantitative
(Congress; needs an API key).  ``fixture`` is a deterministic offline double
used by the tests and for trying the tool without a network.
"""

from __future__ import annotations

from .base import FeedError, TradeFeed

_REGISTRY = {
    "live": "tracker.sources.live:LiveFeed",
    "fixture": "tracker.sources.fixture:FixtureFeed",
}


def available_feeds() -> list[str]:
    return sorted(_REGISTRY)


def get_feed(name: str, config: dict, fresh_cache=None, archive_cache=None) -> TradeFeed:
    key = (name or "").lower()
    if key not in _REGISTRY:
        raise FeedError(f"nieznane źródło {name!r}; dostępne: {', '.join(available_feeds())}")
    module_path, class_name = _REGISTRY[key].split(":")
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)(config, fresh_cache=fresh_cache, archive_cache=archive_cache)


__all__ = ["FeedError", "TradeFeed", "available_feeds", "get_feed"]
