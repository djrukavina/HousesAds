from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.parse import quote, urlencode

from .constants import (
    MAX_ZAGREB_APARTMENT_PRICE_EUR,
    MAX_ZAGREB_PRICE_EUR,
    MIN_ZAGREB_PRICE_EUR,
    WATCH_AREA_INDEX_IDS,
    WATCH_AREA_SLUGS,
)
from .filters import matches_zagreb_apartment, matches_zagreb_house
from .models import Listing

Matcher = Callable[..., bool]


@dataclass(frozen=True)
class Watch:
    id: str
    category: str
    matcher: Matcher
    urls: tuple[str, ...]
    max_pages: int | None = None


def _njuskalo(path: str, **params: object) -> str:
    query = urlencode(params, doseq=True)
    return f"https://www.njuskalo.hr/{path}?{query}" if query else f"https://www.njuskalo.hr/{path}"


def _index_search(category: str, **params: object) -> str:
    """Build an Index search URL.

    Index ignores location/price in the path and in plain query params. The only
    thing it honours is the ``searchQuery`` JSON, which the site itself sends
    percent-encoded twice.
    """
    payload = {"category": category, "module": "nekretnine", **params}
    encoded = quote(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), safe="")
    query = urlencode({"searchQuery": encoded})
    return f"https://www.index.hr/oglasi/nekretnine/{category}/pretraga?{query}"


_ZAGREB_PRICE = {"price[max]": MAX_ZAGREB_PRICE_EUR, "price[min]": MIN_ZAGREB_PRICE_EUR}
_ZAGREB_APARTMENT_PRICE = {
    "price[max]": MAX_ZAGREB_APARTMENT_PRICE_EUR,
    "price[min]": MIN_ZAGREB_PRICE_EUR,
}

_NJUSKALO_HOUSE_URLS = tuple(
    _njuskalo(f"prodaja-kuca/{slug}", **_ZAGREB_PRICE) for slug in WATCH_AREA_SLUGS
)
_NJUSKALO_APARTMENT_URLS = tuple(
    _njuskalo(f"prodaja-stanova/{slug}", **_ZAGREB_APARTMENT_PRICE) for slug in WATCH_AREA_SLUGS
)

_INDEX_HOUSE_URL = _index_search(
    "prodaja-kuca",
    includeCityIds=list(WATCH_AREA_INDEX_IDS),
    priceFrom=MIN_ZAGREB_PRICE_EUR,
    priceTo=MAX_ZAGREB_PRICE_EUR,
)
_INDEX_APARTMENT_URL = _index_search(
    "prodaja-stanova",
    includeCityIds=list(WATCH_AREA_INDEX_IDS),
    priceFrom=MIN_ZAGREB_PRICE_EUR,
    priceTo=MAX_ZAGREB_APARTMENT_PRICE_EUR,
)


def build_watches() -> tuple[Watch, ...]:
    """Watch houses and apartments across the configured areas. Page 1 is enough."""
    return (
        Watch(
            id="zagreb_houses",
            category="Kuće",
            matcher=matches_zagreb_house,
            urls=_NJUSKALO_HOUSE_URLS + (_INDEX_HOUSE_URL,),
            max_pages=1,
        ),
        Watch(
            id="zagreb_apartments",
            category="Stanovi",
            matcher=matches_zagreb_apartment,
            urls=_NJUSKALO_APARTMENT_URLS + (_INDEX_APARTMENT_URL,),
            max_pages=1,
        ),
    )
