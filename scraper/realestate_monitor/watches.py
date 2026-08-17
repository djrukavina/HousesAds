from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlencode

from .constants import MAX_COAST_PRICE_EUR, MAX_ZAGREB_PRICE_EUR
from .filters import matches_coast_house, matches_zagreb_apartment, matches_zagreb_house
from .models import Listing

Matcher = Callable[[Listing], bool]


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


def _index(path: str, **params: object) -> str:
    query = urlencode(params, doseq=True)
    return f"https://www.index.hr{path}?{query}" if query else f"https://www.index.hr{path}"


def build_watches() -> tuple[Watch, ...]:
    """Only the three user filters. Page 1 is enough — new ads appear first."""
    return (
        Watch(
            id="zagreb_houses",
            category="Kuće Zagreb",
            matcher=matches_zagreb_house,
            urls=(
                _njuskalo("prodaja-kuca/zagreb", **{"price[max]": MAX_ZAGREB_PRICE_EUR}),
                _njuskalo("prodaja-kuca/samobor", **{"price[max]": MAX_ZAGREB_PRICE_EUR}),
                _index("/oglasi/nekretnine/prodaja-kuca/zagreb", cijenaDo=MAX_ZAGREB_PRICE_EUR),
            ),
            max_pages=1,
        ),
        Watch(
            id="zagreb_apartments",
            category="Stanovi Zagreb",
            matcher=matches_zagreb_apartment,
            urls=(
                _njuskalo("prodaja-stanova/zagreb", **{"price[max]": MAX_ZAGREB_PRICE_EUR}),
                _index("/oglasi/nekretnine/prodaja-stanova/zagreb", cijenaDo=MAX_ZAGREB_PRICE_EUR),
            ),
            max_pages=1,
        ),
        Watch(
            id="coast_houses",
            category="Kuće otoci",
            matcher=matches_coast_house,
            urls=(
                _njuskalo("prodaja-kuca", **{"price[max]": MAX_COAST_PRICE_EUR}),
                _index("/oglasi/nekretnine/prodaja-kuca", cijenaDo=MAX_COAST_PRICE_EUR),
            ),
            max_pages=1,
        ),
    )
