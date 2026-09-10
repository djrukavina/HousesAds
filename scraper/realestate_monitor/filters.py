from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .constants import (
    EXCLUDED_ZAGREB_AREAS,
    HOUSE_LOCATIONS,
    ISLANDS,
    ISLAND_URL_HINTS,
    MAX_COAST_PRICE_EUR,
    MIN_COAST_PRICE_EUR,
    MAX_ZAGREB_APARTMENT_ROOMS,
    MAX_ZAGREB_PRICE_EUR,
    MIN_ZAGREB_APARTMENT_LIVING_M2,
    MIN_ZAGREB_APARTMENT_ROOMS,
    MIN_ZAGREB_HOUSE_SIZE_M2,
    MIN_ZAGREB_PRICE_EUR,
    NEW_BUILD_KEYWORDS,
    SEA_KEYWORDS,
    ZAGREB_CITY,
    ZAGREB_COUNTY,
)
from .models import Card, Listing


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


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


def is_new_build(text: str, year: Optional[int] = None) -> bool:
    folded = _fold(text)
    if any(keyword in folded for keyword in NEW_BUILD_KEYWORDS):
        return True
    return year is not None and year >= 2024


def is_excluded_zagreb_area(text: str) -> bool:
    folded = _fold(text)
    return any(_fold(token) in folded for token in EXCLUDED_ZAGREB_AREAS)


def is_zagreb_apartment_area(text: str) -> bool:
    """Zagreb city (minus eastern districts) or Zagrebačka županija towns."""
    folded = _fold(text)
    if is_excluded_zagreb_area(folded):
        return False
    if any(_fold(token) in folded for token in ZAGREB_CITY):
        return True
    return any(_fold(token) in folded for token in ZAGREB_COUNTY)


def is_zagreb_area(text: str) -> bool:
    folded = _fold(text)
    if is_excluded_zagreb_area(folded):
        return False
    return any(_fold(token) in folded for token in HOUSE_LOCATIONS)


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


def matches_zagreb_house(listing: Listing) -> bool:
    if listing.price_eur is not None and not _zagreb_price_ok(listing.price_eur):
        return False
    if not is_zagreb_area(listing_blob(listing)):
        return False
    if not _size_at_least(listing, MIN_ZAGREB_HOUSE_SIZE_M2):
        return False
    house_type = listing.house_type
    if house_type == "unknown":
        house_type = classify_house_type(listing_blob(listing))
    if house_type == "detached":
        return True
    if house_type == "row" and (listing.is_new_build or is_new_build(listing_blob(listing))):
        return True
    return False


def matches_zagreb_apartment(listing: Listing) -> bool:
    if listing.price_eur is not None and not _zagreb_price_ok(listing.price_eur):
        return False
    if not is_zagreb_apartment_area(listing_blob(listing)):
        return False
    rooms = listing.rooms or parse_rooms(listing_blob(listing))
    if rooms is None or rooms < MIN_ZAGREB_APARTMENT_ROOMS or rooms >= MAX_ZAGREB_APARTMENT_ROOMS:
        return False
    living = listing.living_m2
    if living is None or living < MIN_ZAGREB_APARTMENT_LIVING_M2:
        return False
    return listing.is_new_build or is_new_build(listing_blob(listing))


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
    if watch_id in ("zagreb_houses", "zagreb_apartments"):
        return _zagreb_price_ok(price_eur)
    if watch_id == "coast_houses":
        return _coast_price_ok(price_eur)
    return True


def prefilter_card(watch_id: str, card: Card) -> bool:
    blob = card_blob(card)
    is_index = card.source == "index"

    if watch_id in ("zagreb_houses", "zagreb_apartments"):
        if not card_price_ok(watch_id, card.price_eur):
            return False
        if watch_id == "zagreb_apartments":
            rooms = parse_rooms(blob)
            if rooms is not None and rooms < MIN_ZAGREB_APARTMENT_ROOMS:
                return False
        # Index search URLs are already location-scoped; card blobs often lack place names.
        if is_index:
            return True
        if watch_id == "zagreb_houses":
            return is_zagreb_area(blob)
        return is_zagreb_apartment_area(blob)

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
