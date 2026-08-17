from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .models import Card, Listing

ZAGREB_CITY = (
    "zagreb",
    "sesvete",
    "podsused",
    "trešnjevka",
    "tresnjevka",
    "dubrava",
    "maksimir",
    "trnje",
    "črnomerec",
    "crnomerec",
    "pečrvo",
    "peščenica",
    "pescenica",
    "stenjevec",
    "podsljeme",
    "brezovica",
    "novi zagreb",
    "donji grad",
    "gornji grad",
    "medveščak",
    "medvescak",
)

ZAGREB_SURROUNDINGS = (
    "zaprešić",
    "zapresic",
    "velika gorica",
    "samobor",
    "dugo selo",
    "sveta nedelja",
    "sveta nedjelja",
    "jastrebarsko",
    "sveti ivan zelina",
    "lučko",
    "lucko",
    "zagrebačka",
    "zagrebacka",
    "okolica",
    "brdovec",
    "rugvica",
    "orihovica",
    "klakar",
    "pusca",
    "pušća",
)

ISLANDS = (
    "krk",
    "cres",
    "lošinj",
    "losinj",
    "mali lošinj",
    "veli lošinj",
    "rab",
    "pag",
    "novalja",
    "brač",
    "brac",
    "hvar",
    "korčula",
    "korcula",
    "vis",
    "mljet",
    "šolta",
    "solta",
    "dugi otok",
    "ugljan",
    "pašman",
    "pasman",
    "čiovo",
    "ciovo",
    "vir",
    "murter",
    "lastovo",
    "iž",
    "silba",
    "ološinj",
    "unije",
    "susak",
    "ilovik",
    "žirje",
    "prvić",
    "prvic",
    "kaprije",
    "zlarin",
    "krapanj",
    "koločep",
    "kolocep",
    "lopud",
    "šipan",
    "sipan",
    "molat",
    "ist",
    "ološ",
    "kornat",
    "žut",
    "pašman",
    "rivanj",
    "sestrunj",
    "oliban",
    "otok",
)

SEA_KEYWORDS = (
    "uz more",
    "do mora",
    "od mora",
    "blizina mora",
    "blizu mora",
    "pogled na more",
    "pogled more",
    "prvi red",
    "1. red",
    "1 red",
    "plaža",
    "plaza",
    "obala",
    "riviera",
    "marina",
    "lučica",
    "lucica",
    "uvali",
    "uvala",
)

NEW_BUILD_KEYWORDS = (
    "novogradnja",
    "nova gradnja",
    "u izgradnji",
    "novograd",
    "new build",
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _blob(listing: Listing) -> str:
    return _fold(f"{listing.title} {listing.location} {listing.description}")


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
    if year is not None and year >= 2024:
        return True
    return False


def is_zagreb_city(text: str) -> bool:
    folded = _fold(text)
    if "zagrebacka" in folded and "zagreb" not in folded:
        return False
    return any(_fold(token) in folded for token in ZAGREB_CITY)


def is_zagreb_area(text: str) -> bool:
    folded = _fold(text)
    return is_zagreb_city(folded) or any(_fold(token) in folded for token in ZAGREB_SURROUNDINGS)


def is_croatian_island(text: str) -> bool:
    folded = _fold(text)
    if "otok" in folded:
        return True
    return any(_fold(name) in folded for name in ISLANDS if name != "otok")


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


def matches_zagreb_house(listing: Listing) -> bool:
    if listing.price_eur is not None and listing.price_eur > 300_000:
        return False
    if not is_zagreb_area(_blob(listing)):
        return False
    if listing.yard_m2 is None or listing.yard_m2 < 100:
        return False
    house_type = listing.house_type
    if house_type == "unknown":
        house_type = classify_house_type(_blob(listing))
    if house_type == "detached":
        return True
    if house_type == "row" and listing.is_new_build:
        return True
    return False


def matches_zagreb_apartment(listing: Listing) -> bool:
    if listing.price_eur is not None and listing.price_eur > 300_000:
        return False
    if not is_zagreb_city(_blob(listing)):
        return False
    rooms = listing.rooms or parse_rooms(_blob(listing))
    if rooms is None or rooms < 3:
        return False
    if listing.is_new_build or is_new_build(_blob(listing)):
        return True
    return 3 <= rooms < 4


def prefilter_card(watch_id: str, card: Card) -> bool:
    blob = f"{card.title} {card.location} {card.snippet}"
    if watch_id == "zagreb_houses":
        if card.price_eur is not None and card.price_eur > 300_000:
            return False
        return is_zagreb_area(blob)
    if watch_id == "zagreb_apartments":
        if card.price_eur is not None and card.price_eur > 300_000:
            return False
        rooms = parse_rooms(blob)
        if rooms is not None and rooms < 3:
            return False
        return is_zagreb_city(blob)
    if watch_id == "coast_houses":
        if card.price_eur is not None and card.price_eur > 50_000:
            return False
        return is_croatian_island(blob) or any(
            hint in card.url
            for hint in (
                "/krk",
                "/cres",
                "/losinj",
                "/rab",
                "/pag",
                "/novalja",
                "/brac",
                "/hvar",
                "/korcula",
                "/vis",
                "/mljet",
                "/solta",
                "/dugi-otok",
                "/ugljan",
                "/pasman",
                "/ciovo",
                "/vir",
                "/murter",
                "/lastovo",
            )
        )
    return True


def matches_coast_house(listing: Listing) -> bool:
    if listing.price_eur is None or listing.price_eur > 50_000:
        return False
    blob = _blob(listing)
    if not is_croatian_island(blob):
        return False
    return listing.near_sea or is_near_sea(blob)
