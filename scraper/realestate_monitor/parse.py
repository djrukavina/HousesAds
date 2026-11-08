from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .constants import MIN_ZAGREB_APARTMENT_BUILD_YEAR, MIN_ZAGREB_HOUSE_BUILD_YEAR
from .filters import (
    classify_house_type,
    is_near_sea,
    is_new_build,
    parse_price,
    parse_rooms,
    parse_square_meters,
)
from .models import Card, Listing

NJUSKALO_ORIGIN = "https://www.njuskalo.hr"
INDEX_ORIGIN = "https://www.index.hr"
INDEX_LISTING_URL_RE = re.compile(
    r"https?://www\.index\.hr(/oglasi/nekretnine/[^\"'\s<>]+/oglas/[^\"'\s<>]+/\d{5,})"
)


def parse_njuskalo_cards(html: str) -> list[Card]:
    soup = BeautifulSoup(html, "lxml")
    items: list[Card] = []
    containers = []
    for class_name in ("EntityList--ListItemRegularAd", "EntityList--VauVau", "EntityList--Standard"):
        found = soup.find("div", class_=class_name)
        if found:
            containers.append(found)
    entities = []
    if containers:
        for container in containers:
            entities.extend(container.select("li.EntityList-item"))
    else:
        entities = soup.select("li.EntityList-item")

    seen: set[str] = set()
    for entity in entities:
        if entity.find("article", class_="entity-body") is None:
            continue
        link = entity.find("a", href=True)
        if link is None:
            continue
        href = urljoin(NJUSKALO_ORIGIN, link["href"])
        external_id = _njuskalo_id(href)
        if not external_id or external_id in seen:
            continue
        seen.add(external_id)
        title = " ".join(link.get_text(" ", strip=True).split())
        desc_node = entity.find("div", class_="entity-description-main")
        snippet = desc_node.get_text(" ", strip=True) if desc_node else ""
        location = _location_from_snippet(snippet)
        price_node = entity.find("strong", class_=re.compile(r"price"))
        price_text = price_node.get_text(" ", strip=True) if price_node else entity.get_text(" ", strip=True)
        image = entity.find("img")
        items.append(
            Card(
                source="njuskalo",
                external_id=external_id,
                title=title,
                url=href,
                price_eur=parse_price(price_text),
                location=location,
                snippet=snippet,
                image_url=image.get("src") if image and image.get("src") else None,
            )
        )
    return items


def listing_from_njuskalo_detail(card: Card, html: str, watch_id: str, category: str) -> Listing:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    merged = f"{card.title}\n{card.snippet}\n{text}"
    year = _parse_year(merged)
    return Listing(
        id=f"njuskalo:{card.external_id}",
        source="njuskalo",
        watch_id=watch_id,
        title=card.title,
        url=card.url,
        price_eur=card.price_eur if card.price_eur is not None else parse_price(merged),
        location=card.location or _location_from_snippet(merged),
        category=category,
        description=card.snippet or _meta_description(soup),
        image_url=card.image_url,
        posted_at_millis=_posted_millis(soup),
        house_type=classify_house_type(merged),
        rooms=parse_rooms(merged),
        yard_m2=parse_square_meters(
            merged,
            ("povrsina okucnice", "okucnica", "povrsina parcele", "parcela", "vrt"),
        ),
        living_m2=parse_square_meters(merged, ("stambena povrsina", "stambena povrsina", "povrsina")),
        is_new_build=is_new_build(
            merged, year, min_year=_build_year_min(watch_id)
        ),
        near_sea=is_near_sea(merged),
    )


def _build_year_min(watch_id: str) -> int:
    if watch_id == "zagreb_houses":
        return MIN_ZAGREB_HOUSE_BUILD_YEAR
    return MIN_ZAGREB_APARTMENT_BUILD_YEAR


def parse_index_cards(html: str) -> list[Card]:
    soup = BeautifulSoup(html, "lxml")
    items: list[Card] = []
    seen: set[str] = set()

    for link in soup.select("a[href]"):
        href = urljoin(INDEX_ORIGIN, link.get("href", ""))
        card = _index_card_from_url(href, link, seen)
        if card is not None:
            items.append(card)

    if not items:
        for match in INDEX_LISTING_URL_RE.finditer(html):
            href = urljoin(INDEX_ORIGIN, match.group(1))
            card = _index_card_from_url(href, None, seen)
            if card is not None:
                items.append(card)

    return items


def _index_card_from_url(href: str, link, seen: set[str]) -> Card | None:
    external_id = _index_id(href)
    if not external_id or external_id in seen:
        return None
    if "/nekretnine/" not in href or "/oglas/" not in href:
        return None

    title = ""
    if link is not None:
        title = " ".join(link.get_text(" ", strip=True).split())
        if len(title) < 8:
            title = " ".join((link.get("title") or link.get("aria-label") or "").split())
    if len(title) < 8:
        slug = urlparse(href).path.rsplit("/", 1)[0].rsplit("/", 1)[-1]
        title = slug.replace("-", " ").strip().title()

    seen.add(external_id)
    card_root = _index_card_root(link)
    blob = card_root.get_text(" ", strip=True) if card_root is not None else title
    image = card_root.find("img") if card_root is not None and hasattr(card_root, "find") else None
    return Card(
        source="index",
        external_id=external_id,
        title=title,
        url=href.split("?")[0],
        price_eur=parse_price(blob),
        location=_guess_index_location(blob, title),
        snippet=blob[:500],
        image_url=image.get("src") if image is not None and image.get("src") else None,
    )


def _index_card_root(link):
    """Walk up from the listing link to a richer card container."""
    if link is None:
        return None
    node = link
    best = None
    for _ in range(8):
        parent = getattr(node, "parent", None)
        if parent is None or not getattr(parent, "name", None):
            break
        text = parent.get_text(" ", strip=True)
        if len(text) > 40:
            best = parent
            if parent.name in ("article", "li") or len(text) > 140:
                return parent
        node = parent
    return best or link.find_parent(["article", "li", "div"])


def listing_from_index_detail(card: Card, html: str, watch_id: str, category: str) -> Listing:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    merged = f"{card.title}\n{card.snippet}\n{text}"
    year = _parse_year(merged)
    location = card.location.strip() if card.location else ""
    if not location or len(location) < 3:
        location = _guess_index_location(merged, card.title)
    # Keep enough detail text so location / novogradnja keywords reach the matcher.
    description = f"{card.snippet}\n{text}".strip()[:2000]
    return Listing(
        id=f"index:{card.external_id}",
        source="index",
        watch_id=watch_id,
        title=card.title,
        url=card.url,
        price_eur=card.price_eur if card.price_eur is not None else parse_price(merged),
        location=location,
        category=category,
        description=description,
        image_url=card.image_url,
        posted_at_millis=_posted_millis(soup),
        house_type=classify_house_type(merged),
        rooms=parse_rooms(merged),
        yard_m2=parse_square_meters(
            merged,
            ("okucnica", "povrsina okucnice", "parcela", "vrt", "zemljiste"),
        ),
        living_m2=parse_square_meters(
            merged,
            ("stambena povrsina", "stambeni prostor", "kvadratura", "povrsina stana", "m2", "m²"),
        ),
        is_new_build=is_new_build(
            merged, year, min_year=_build_year_min(watch_id)
        ),
        near_sea=is_near_sea(merged),
    )


def _njuskalo_id(url: str) -> Optional[str]:
    match = re.search(r"oglas-(\d+)", url)
    if match:
        return match.group(1)
    path = urlparse(url).path.rstrip("/")
    if path:
        return path.split("/")[-1]
    return None


def _index_id(url: str) -> Optional[str]:
    path = urlparse(url).path
    match = re.search(r"/oglas/[^/]+/(\d{5,})", path)
    if match:
        return match.group(1)
    match = re.search(r"/(\d{5,})/?$", path)
    if match:
        return match.group(1)
    match = re.search(r"oglas-(\d+)", url)
    return match.group(1) if match else None


def _location_from_snippet(snippet: str) -> str:
    match = re.search(r"Lokacija:\s*(.+)", snippet)
    if match:
        return match.group(1).split("Objavljen")[0].strip()
    return snippet[:80]


def _guess_index_location(blob: str, title: str) -> str:
    match = re.search(r"\d{2}\.\d{2}\.\d{4}\.\s*\|\s*([^0-9€]+)", blob)
    if match:
        return match.group(1).strip()
    return title.split(",")[0].strip()


def _meta_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content", "") if tag else ""


def _posted_millis(soup: BeautifulSoup) -> int:
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        from datetime import datetime

        raw = time_tag["datetime"].replace("Z", "+00:00")
        try:
            return int(datetime.fromisoformat(raw).timestamp() * 1000)
        except ValueError:
            pass
    return 0


def _parse_year(text: str) -> Optional[int]:
    match = re.search(r"godina izgradnje\s*:?\s*(20\d{2})", text.lower())
    if match:
        return int(match.group(1))
    match = re.search(r"\b(202[4-9]|2030)\b", text)
    return int(match.group(1)) if match else None
