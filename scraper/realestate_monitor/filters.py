from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .constants import (
    ISLANDS,
    ISLAND_URL_HINTS,
    MAX_COAST_PRICE_EUR,
    MIN_COAST_PRICE_EUR,
    MAX_ZAGREB_APARTMENT_PRICE_EUR,
    MAX_ZAGREB_PRICE_EUR,
    MIN_ZAGREB_APARTMENT_BUILD_YEAR,
    MIN_ZAGREB_APARTMENT_LIVING_M2,
    MIN_ZAGREB_HOUSE_BUILD_YEAR,
    MIN_ZAGREB_HOUSE_SIZE_M2,
    MIN_ZAGREB_PRICE_EUR,
    NEW_BUILD_KEYWORDS,
    SEA_KEYWORDS,
    WATCH_AREA_NAMES,
)
from .models import Card, Listing


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _area_key(text: str) -> str:
    """Fold diacritics and punctuation so ``Novi Zagreb - Istok`` matches ``novi zagreb istok``."""
    return re.sub(r"[^a-z0-9]+", " ", _fold(text)).strip()


_WATCH_AREA_KEYS = tuple(_area_key(name) for name in WATCH_AREA_NAMES)


def listing_blob(listing: Listing) -> str:
    return _fold(f"{listing.title} {listing.location} {listing.description}")


def card_blob(card: Card) -> str:
    return _fold(f"{card.title} {card.location} {card.snippet}")


def parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    folded = text.lower().replace("\xa0", " ")
    if "po dogovoru" in folded or "dogovor" in folded:
        return None
    match = re.search(r"(\d{1,3}(?:[.\s]\d{3})+|\d+)(?:[.,]\d+)?\s*€", text)
    if not match:
        match = re.search(r"(\d{1,3}(?:[.\s]\d{3})+|\d+)", text)
    if not match:
        return None
    raw = match.group(1).replace(".", "").replace(" ", "")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_rooms(text: str) -> Optional[float]:
    folded = _fold(text)
    if "trosoban" in folded or "troso" in folded:
        return 3.0
    match = re.search(r"(\d+(?:[.,]5)?)\s*-?\s*sobn", folded)
    if match:
        return float(match.group(1).replace(",", "."))
    match = re.search(r"broj soba\s*:?\s*(\d+(?:[.,]5)?)", folded)
    if match:
        return float(match.group(1).replace(",", "."))
    return None


def parse_square_meters(text: str, labels: tuple[str, ...]) -> Optional[float]:
    folded = _fold(text)
    for label in labels:
        pattern = rf"{label}\s*:?\s*(\d+(?:[.,]\d+)?)"
        match = re.search(pattern, folded)
        if match:
            return float(match.group(1).replace(",", "."))
    return None


def classify_house_type(text: str) -> str:
    folded = _fold(text)
    if "u nizu" in folded or "niz" in folded:
        return "row"
    if "samostoj" in folded:
        return "detached"
    if "dvojn" in folded or "duplex" in folded:
        return "duplex"
    return "unknown"


def is_new_build(text: str, year: Optional[int] = None, *, min_year: int) -> bool:
    folded = _fold(text)
    if any(keyword in folded for keyword in NEW_BUILD_KEYWORDS):
        return True
    return year is not None and year >= min_year


def is_watched_area(text: str) -> bool:
    """True when the listing location belongs to one of the configured watch areas."""
    padded = f" {_area_key(text)} "
    return any(f" {token} " in padded for token in _WATCH_AREA_KEYS)


def is_croatian_island(text: str) -> bool:
    folded = _fold(text)
    if re.search(r"\botok\b", folded):
        return True
    for name in ISLANDS:
        if name == "otok":
            continue
        token = _fold(name)
        if len(token) <= 3:
            if re.search(rf"\b{re.escape(token)}\b", folded):
                return True
        elif token in folded:
            return True
    return False


def is_near_sea(text: str) -> bool:
    folded = _fold(text)
    if any(keyword in folded for keyword in SEA_KEYWORDS):
        distance = re.search(r"(\d+)\s*(m|km)\s*(od mora|do mora|do plaze|od plaze)", folded)
        if distance:
            value = float(distance.group(1))
            unit = distance.group(2)
            meters = value * 1000 if unit == "km" else value
            return meters <= 1500
        return True
    return False


def _size_at_least(listing: Listing, minimum: float) -> bool:
    living = listing.living_m2
    yard = listing.yard_m2
    if living is None and yard is None:
        return False
    return (living is not None and living >= minimum) or (yard is not None and yard >= minimum)


def _zagreb_price_ok(price_eur: Optional[float]) -> bool:
    if price_eur is None:
        return True
    return MIN_ZAGREB_PRICE_EUR <= price_eur <= MAX_ZAGREB_PRICE_EUR


def _zagreb_apartment_price_ok(price_eur: Optional[float]) -> bool:
    if price_eur is None:
        return True
    return MIN_ZAGREB_PRICE_EUR <= price_eur <= MAX_ZAGREB_APARTMENT_PRICE_EUR


def matches_zagreb_house(listing: Listing, url_scoped: bool = False) -> bool:
    if listing.price_eur is not None and not _zagreb_price_ok(listing.price_eur):
        return False
    blob = listing_blob(listing)
    index_soft = listing.source == "index"
    # Per-area search URLs already restrict the location; listing text often names
    # only a neighbourhood (e.g. "Zagreb (Blato)") that would fail the area match.
    if not url_scoped and not is_watched_area(blob) and not index_soft:
        return False
    if not _size_at_least(listing, MIN_ZAGREB_HOUSE_SIZE_M2):
        # Index detail pages often omit clear yard/living m² fields.
        if not (index_soft and listing.living_m2 is None and listing.yard_m2 is None):
            return False
    built_recently = listing.is_new_build or is_new_build(
        blob, min_year=MIN_ZAGREB_HOUSE_BUILD_YEAR
    )
    if not built_recently and not index_soft:
        return False
    house_type = listing.house_type
    if house_type == "unknown":
        house_type = classify_house_type(blob)
    if house_type == "detached":
        return True
    if house_type == "row":
        return True
    # Index rarely labels "samostojna" / "u nizu" — keep if price + location already match.
    if index_soft and house_type == "unknown":
        return True
    return False


def matches_zagreb_apartment(listing: Listing, url_scoped: bool = False) -> bool:
    if listing.price_eur is not None and not _zagreb_apartment_price_ok(listing.price_eur):
        return False
    blob = listing_blob(listing)
    index_soft = listing.source == "index"
    if not url_scoped and not is_watched_area(blob) and not index_soft:
        return False
    living = listing.living_m2
    if living is None:
        if not index_soft:
            return False
    elif living < MIN_ZAGREB_APARTMENT_LIVING_M2:
        return False
    if listing.is_new_build or is_new_build(
        blob, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR
    ):
        return True
    # Index often omits explicit novogradnja wording even for newer builds.
    return index_soft


def _coast_price_ok(price_eur: Optional[float]) -> bool:
    if price_eur is None:
        return False
    return MIN_COAST_PRICE_EUR <= price_eur <= MAX_COAST_PRICE_EUR


def matches_coast_house(listing: Listing) -> bool:
    if not _coast_price_ok(listing.price_eur):
        return False
    blob = listing_blob(listing)
    if not is_croatian_island(blob):
        return False
    return listing.near_sea or is_near_sea(blob)


def card_price_ok(watch_id: str, price_eur: Optional[float]) -> bool:
    if watch_id == "zagreb_houses":
        return _zagreb_price_ok(price_eur)
    if watch_id == "zagreb_apartments":
        return _zagreb_apartment_price_ok(price_eur)
    if watch_id == "coast_houses":
        return _coast_price_ok(price_eur)
    return True


def _card_year(blob: str) -> Optional[int]:
    match = re.search(r"godina izgradnje\s*:?\s*((?:19|20)\d{2})", blob)
    return int(match.group(1)) if match else None


def _njuskalo_card_viable(watch_id: str, blob: str) -> bool:
    """Drop Njuškalo cards only when their own text proves they cannot match.

    Detail pages carry the complete data, so anything unclear stays for hydration.
    """
    if watch_id == "zagreb_apartments":
        living = parse_square_meters(blob, ("stambena povrsina", "povrsina stana"))
        if living is not None and living < MIN_ZAGREB_APARTMENT_LIVING_M2:
            return False
        year = _card_year(blob)
        if (
            year is not None
            and year < MIN_ZAGREB_APARTMENT_BUILD_YEAR
            and not is_new_build(blob, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR)
        ):
            return False
        return True

    if watch_id == "zagreb_houses":
        living = parse_square_meters(blob, ("stambena povrsina", "stambeni prostor"))
        yard = parse_square_meters(blob, ("povrsina okucnice", "okucnica", "povrsina parcele"))
        if (
            living is not None
            and yard is not None
            and max(living, yard) < MIN_ZAGREB_HOUSE_SIZE_M2
        ):
            return False
        if classify_house_type(blob) == "duplex":
            return False
        year = _card_year(blob)
        if (
            year is not None
            and year < MIN_ZAGREB_HOUSE_BUILD_YEAR
            and not is_new_build(blob, min_year=MIN_ZAGREB_HOUSE_BUILD_YEAR)
        ):
            return False
        return True

    return True


def prefilter_card(watch_id: str, card: Card, url_scoped: bool = False) -> bool:
    blob = card_blob(card)
    is_index = card.source == "index"

    if watch_id in ("zagreb_houses", "zagreb_apartments"):
        if not card_price_ok(watch_id, card.price_eur):
            return False
        if card.source == "njuskalo" and not _njuskalo_card_viable(watch_id, blob):
            return False
        # Search URLs are location-scoped; card blobs often name only a neighbourhood.
        if url_scoped or is_index:
            return True
        return is_watched_area(blob)

    if watch_id == "coast_houses":
        if card.price_eur is not None and not _coast_price_ok(card.price_eur):
            return False
        # Index cards rarely expose island/price text or Njuškalo-style URL hints — hydrate first.
        if is_index:
            return True
        if not card_price_ok(watch_id, card.price_eur):
            return False
        return is_croatian_island(blob) or any(hint in card.url for hint in ISLAND_URL_HINTS)

    return True
