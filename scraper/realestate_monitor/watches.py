from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlencode

from .constants import MAX_COAST_PRICE_EUR, MAX_ZAGREB_PRICE_EUR, MIN_COAST_PRICE_EUR, MIN_ZAGREB_PRICE_EUR
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


_ZAGREB_PRICE = {"price[max]": MAX_ZAGREB_PRICE_EUR, "price[min]": MIN_ZAGREB_PRICE_EUR}
_INDEX_ZAGREB_PRICE = {"cijenaDo": MAX_ZAGREB_PRICE_EUR, "cijenaOd": MIN_ZAGREB_PRICE_EUR}
_COAST_PRICE = {"price[max]": MAX_COAST_PRICE_EUR, "price[min]": MIN_COAST_PRICE_EUR}
_INDEX_COAST_PRICE = {"cijenaDo": MAX_COAST_PRICE_EUR, "cijenaOd": MIN_COAST_PRICE_EUR}


def build_watches() -> tuple[Watch, ...]:
    """Only the three user filters. Page 1 is enough — new ads appear first."""
    return (
        Watch(
            id="zagreb_houses",
            category="Kuće Zagreb",
            matcher=matches_zagreb_house,
            urls=(
                _njuskalo("prodaja-kuca/zagreb", **_ZAGREB_PRICE),
                _njuskalo("prodaja-kuca/samobor", **_ZAGREB_PRICE),
                _index("/oglasi/nekretnine/prodaja-kuca/zagreb", **_INDEX_ZAGREB_PRICE),
            ),
            max_pages=1,
        ),
        Watch(
            id="zagreb_apartments",
            category="Stanovi Zagreb",
            matcher=matches_zagreb_apartment,
            urls=(
                _njuskalo("prodaja-stanova/zagreb", **_ZAGREB_PRICE),
                _njuskalo("prodaja-stanova/velika-gorica", **_ZAGREB_PRICE),
                _njuskalo("prodaja-stanova/zapresic", **_ZAGREB_PRICE),
                _njuskalo("prodaja-stanova/samobor", **_ZAGREB_PRICE),
                _njuskalo("prodaja-stanova/dugo-selo", **_ZAGREB_PRICE),
                _njuskalo("prodaja-stanova/sveta-nedelja", **_ZAGREB_PRICE),
                _index("/oglasi/nekretnine/prodaja-stanova/zagreb", **_INDEX_ZAGREB_PRICE),
                _index("/oglasi/nekretnine/prodaja-stanova/velika-gorica", **_INDEX_ZAGREB_PRICE),
                _index("/oglasi/nekretnine/prodaja-stanova/zapresic", **_INDEX_ZAGREB_PRICE),
                _index("/oglasi/nekretnine/prodaja-stanova/samobor", **_INDEX_ZAGREB_PRICE),
            ),
            max_pages=1,
        ),
        Watch(
            id="coast_houses",
            category="Kuće otoci",
            matcher=matches_coast_house,
            urls=(
                _njuskalo("prodaja-kuca", **_COAST_PRICE),
                _index("/oglasi/nekretnine/prodaja-kuca", **_INDEX_COAST_PRICE),
            ),
            max_pages=1,
        ),
    )
