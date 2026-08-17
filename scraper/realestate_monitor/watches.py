from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlencode

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


ISLAND_SLUGS = (
    "krk",
    "cres",
    "mali-losinj",
    "rab",
    "pag",
    "novalja",
    "brac",
    "hvar",
    "korcula",
    "vis",
    "mljet",
    "solta",
    "dugi-otok",
    "ugljan",
    "pasman",
    "ciovo",
    "vir",
    "murter",
    "lastovo",
)


def build_watches() -> tuple[Watch, ...]:
    island_urls = tuple(
        _njuskalo(f"prodaja-kuca/{slug}", **{"price[max]": 50000})
        for slug in ISLAND_SLUGS
    ) + (
        _njuskalo("prodaja-kuca", **{"price[max]": 50000}),
        _index("/oglasi/nekretnine/prodaja-kuca", cijenaDo=50000),
    )
    return (
        Watch(
            id="zagreb_houses",
            category="Kuće Zagreb",
            matcher=matches_zagreb_house,
            urls=(
                _njuskalo("prodaja-kuca/zagreb", **{"price[max]": 300000}),
                _njuskalo("prodaja-kuca/zagrebacka", **{"price[max]": 300000}),
                _index("/oglasi/nekretnine/prodaja-kuca/zagreb", cijenaDo=300000),
            ),
        ),
        Watch(
            id="zagreb_apartments",
            category="Stanovi Zagreb",
            matcher=matches_zagreb_apartment,
            urls=(
                _njuskalo("prodaja-stanova/zagreb", **{"price[max]": 300000}),
                _index("/oglasi/nekretnine/prodaja-stanova/zagreb", cijenaDo=300000),
            ),
        ),
        Watch(
            id="coast_houses",
            category="Kuće otoci",
            matcher=matches_coast_house,
            urls=island_urls,
            max_pages=1,
        ),
    )
