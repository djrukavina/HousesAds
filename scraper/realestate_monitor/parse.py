from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .constants import MIN_ZAGREB_APARTMENT_BUILD_YEAR, MIN_ZAGREB_HOUSE_BUILD_YEAR
from .filters import (
    _fold,
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


def _initial_state(html: str) -> dict:
    """Extract the server-rendered Vue state Njuškalo embeds in the page."""
    match = re.search(
        r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});?\s*</script>",
        html,
        re.S,
    )
    if not match:
        return {}
    try:
        state = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return state if isinstance(state, dict) else {}


def _njuskalo_cards_from_state(html: str) -> list[Card]:
    state = _initial_state(html)
    page = (state.get("browseListingsStore") or {}).get("pageData") or {}
    cards: list[Card] = []
    seen: set[str] = set()
    for key in (
        "regularListings",
        "promotedListings",
        "userPromotedListings",
        "superVauListings",
    ):
        for item in page.get(key) or []:
            if not isinstance(item, dict):
                continue
            card = _njuskalo_card_from_item(item)
            if card is None or card.external_id in seen:
                continue
            seen.add(card.external_id)
            cards.append(card)
    return cards


def _njuskalo_card_from_item(item: dict) -> Card | None:
    raw_url = str(item.get("url") or "").strip()
    if not raw_url:
        return None
    url = urljoin(NJUSKALO_ORIGIN, raw_url)
    external_id = str(item.get("id") or _njuskalo_id(url) or "").strip()
    if not external_id:
        return None
    title = " ".join(str(item.get("title") or "").split())
    if len(title) < 3:
        return None

    abstracts = [a for a in (item.get("abstracts") or []) if isinstance(a, dict)]
    highlights = [h for h in (item.get("highlights") or []) if isinstance(h, dict)]
    parts = [str(a.get("value") or "") for a in abstracts]
    parts.extend(f"{h.get('label')}: {h.get('value')}" for h in highlights)
    snippet = " | ".join(part for part in parts if part)[:500]

    location = str(item.get("location") or "").strip()
    if not location:
        for abstract in abstracts:
            if _fold(str(abstract.get("caption") or "")) == "lokacija":
                location = str(abstract.get("value") or "").strip()
                break

    price: Optional[float] = None
    if not item.get("isPriceOnRequest") and not item.get("hidePrice"):
        price = parse_price(str(item.get("priceFormatted") or ""))
        raw_price = item.get("price")
        if price is None and isinstance(raw_price, (int, float)):
            price = float(raw_price)

    image = item.get("image")
    image_url = None
    if isinstance(image, str):
        image_url = image
    elif isinstance(image, dict):
        image_url = image.get("url") or image.get("previewUrl") or image.get("thumbnailUrl")

    return Card(
        source="njuskalo",
        external_id=external_id,
        title=title,
        url=url,
        price_eur=price,
        location=location,
        snippet=snippet,
        image_url=image_url,
    )


def parse_njuskalo_cards(html: str) -> list[Card]:
    state_cards = _njuskalo_cards_from_state(html)
    if state_cards:
        return state_cards

    # Legacy markup parser, kept for cached/older pages without the Vue state.
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


def _njuskalo_page_data(html: str) -> dict:
    state = _initial_state(html)
    page = (state.get("listingDetailStore") or {}).get("pageData")
    return page if isinstance(page, dict) else {}


def _box_items(page: dict, name: str) -> list[dict]:
    box = (page.get("boxes") or {}).get(name) or {}
    if not isinstance(box, dict):
        return []
    return [item for item in (box.get("items") or []) if isinstance(item, dict)]


def _basic_details(page: dict) -> dict[str, str]:
    details: dict[str, str] = {}
    for item in _box_items(page, "basicDetailsBox"):
        field = str(item.get("fieldName") or "").strip()
        value = item.get("definition")
        if field and value is not None:
            details[field] = str(value).strip()
    return details


def _state_year(page: dict, details: dict[str, str]) -> Optional[int]:
    """Read the build year only from labelled fields, never from dates in the text."""
    candidates = [
        details.get("yearOfConstruction"),
        details.get("buildYear"),
        details.get("yearBuilt"),
    ]
    for item in _box_items(page, "highlightedDetailsBox"):
        if _fold(str(item.get("label") or "")) == "godina izgradnje":
            candidates.append(item.get("value"))
    for value in candidates:
        match = re.search(r"\b((?:19|20)\d{2})\b", str(value or ""))
        if match:
            return int(match.group(1))
    return None


def _first_number(value: object) -> Optional[float]:
    """Parse Croatian-formatted sizes such as ``1.424,00 m²`` or ``94,00 m²``."""
    if value is None:
        return None
    match = re.search(r"\d[\d.,\s]*", str(value))
    if not match:
        return None
    raw = match.group(0).strip().replace(" ", "")
    if not raw:
        return None
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        raw = raw.replace(".", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _flatten_box_item(item: object, parts: list[str]) -> None:
    if not isinstance(item, dict):
        return
    key = str(item.get("key") or item.get("label") or "").strip()
    children = item.get("items")
    if isinstance(children, list) and children:
        if key:
            parts.append(key)
        for child in children:
            _flatten_box_item(child, parts)
        return

    values = item.get("values")
    if isinstance(values, list) and values:
        rendered = []
        for value in values:
            if isinstance(value, dict):
                child_key = str(value.get("key") or "").strip()
                child_value = value.get("value")
                if child_key and child_value is not None:
                    rendered.append(f"{child_key}: {child_value}")
                elif child_value is not None:
                    rendered.append(str(child_value))
            elif value is not None:
                rendered.append(str(value))
        joined = ", ".join(part for part in rendered if part)
        if joined:
            parts.append(f"{key}: {joined}" if key else joined)
        return

    value = item.get("value")
    if value is None:
        value = item.get("definition")
    if value is not None:
        parts.append(f"{key}: {value}" if key else str(value))


def _njuskalo_state_text(page: dict) -> str:
    parts: list[str] = []
    description = (page.get("boxes") or {}).get("detailDescriptionBox") or {}
    if isinstance(description, dict) and description.get("text"):
        parts.append(str(description["text"]))
    for name in ("highlightedDetailsBox", "basicDetailsBox"):
        for item in _box_items(page, name):
            label = str(item.get("label") or "").strip()
            value = item.get("value")
            if value is None:
                value = item.get("definition")
            if label and value is not None:
                parts.append(f"{label}: {value}")
    for item in _box_items(page, "additionalDetailsBox"):
        _flatten_box_item(item, parts)
    return "\n".join(parts)


def _iso_millis(value: object) -> int:
    if not value:
        return 0
    try:
        return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError:
        return 0


def _listing_from_njuskalo_state(
    card: Card, page: dict, watch_id: str, category: str
) -> Listing:
    listing = page.get("listing") if isinstance(page.get("listing"), dict) else {}
    details = _basic_details(page)
    year = _state_year(page, details)
    text = _njuskalo_state_text(page)
    merged = f"{card.title}\n{card.snippet}\n{text}"

    title = " ".join(str(listing.get("title") or card.title).split())
    url = urljoin(NJUSKALO_ORIGIN, str(listing.get("url") or card.url))
    location = details.get("location") or card.location or _location_from_snippet(merged)

    price: Optional[float] = None
    if not listing.get("isPriceOnRequest") and not listing.get("hidePrice"):
        raw_price = listing.get("price")
        if isinstance(raw_price, (int, float)):
            price = float(raw_price)
        else:
            price = parse_price(str(listing.get("priceFormatted") or ""))
    if price is None:
        price = card.price_eur if card.price_eur is not None else parse_price(merged)

    image_url = None
    photos = (page.get("media") or {}).get("photos") or []
    for photo in photos:
        if isinstance(photo, dict):
            image_url = (
                photo.get("previewUrl")
                or photo.get("fullUrl")
                or photo.get("thumbnailUrl")
            )
            if image_url:
                break
    if not image_url:
        raw_image = listing.get("image")
        image_url = raw_image if isinstance(raw_image, str) else card.image_url

    living_m2 = _first_number(details.get("livingArea"))
    if living_m2 is None:
        living_m2 = parse_square_meters(
            merged, ("stambena povrsina", "povrsina stana", "kvadratura")
        )
    yard_m2 = _first_number(details.get("yardArea"))
    if yard_m2 is None:
        yard_m2 = parse_square_meters(
            merged, ("povrsina okucnice", "okucnica", "povrsina parcele", "parcela")
        )

    house_type = classify_house_type(str(details.get("houseBuildingType") or ""))
    if house_type == "unknown":
        house_type = classify_house_type(merged)

    rooms = parse_rooms(str(details.get("numberOfRooms") or ""))
    if rooms is None:
        rooms = parse_rooms(merged)

    description = ""
    description_box = (page.get("boxes") or {}).get("detailDescriptionBox") or {}
    if isinstance(description_box, dict):
        description = str(description_box.get("text") or "").strip()
    if not description:
        description = card.snippet or text

    return Listing(
        id=f"njuskalo:{card.external_id}",
        source="njuskalo",
        watch_id=watch_id,
        title=title,
        url=url,
        price_eur=price,
        location=location,
        category=category,
        description=description,
        image_url=image_url,
        posted_at_millis=_iso_millis(listing.get("createdAt")),
        house_type=house_type,
        rooms=rooms,
        yard_m2=yard_m2,
        living_m2=living_m2,
        is_new_build=is_new_build(merged, year, min_year=_build_year_min(watch_id)),
        near_sea=is_near_sea(merged),
    )


def listing_from_njuskalo_detail(card: Card, html: str, watch_id: str, category: str) -> Listing:
    page = _njuskalo_page_data(html)
    if page.get("listing") or page.get("boxes"):
        return _listing_from_njuskalo_state(card, page, watch_id, category)

    # Fallback for pages that do not expose the Vue state.
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    merged = f"{card.title}\n{card.snippet}\n{text}"
    year = _labeled_year(merged)
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


def _class_text(node, token: str) -> str:
    if node is None or not hasattr(node, "select_one"):
        return ""
    element = node.select_one(f'[class*="{token}"]')
    if element is None:
        return ""
    return " ".join(element.get_text(" ", strip=True).split())


def _index_card_image(card_root) -> Optional[str]:
    if card_root is None:
        return None
    for element in card_root.find_all(style=True):
        match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', element.get("style", ""))
        if match:
            return match.group(1)
    image = card_root.find("img") if hasattr(card_root, "find") else None
    src = image.get("src") if image is not None else None
    return src or None


def _index_card_from_url(href: str, link, seen: set[str]) -> Card | None:
    external_id = _index_id(href)
    if not external_id or external_id in seen:
        return None
    if "/nekretnine/" not in href or "/oglas/" not in href:
        return None

    card_root = _index_card_root(link)
    title = ""
    if link is not None:
        title = " ".join((link.get("title") or "").split())
        if not title:
            title = _class_text(card_root, "AdSummary__title")
        if not title:
            title = " ".join(link.get_text(" ", strip=True).split())
    if not title:
        title = _class_text(card_root, "AdSummary__title")
    if not title:
        slug = urlparse(href).path.rsplit("/", 1)[0].rsplit("/", 1)[-1]
        title = slug.replace("-", " ").strip().title()

    blob = " ".join(card_root.get_text(" ", strip=True).split()) if card_root is not None else title
    price_text = _class_text(card_root, "adPrice__price")
    location = _class_text(card_root, "adLocation__location")
    if not location:
        location = _guess_index_location(blob, title)

    seen.add(external_id)
    return Card(
        source="index",
        external_id=external_id,
        title=title,
        url=href.split("?")[0],
        price_eur=parse_price(price_text or blob),
        location=location,
        snippet=blob[:500],
        image_url=_index_card_image(card_root),
    )


def _index_card_root(link):
    """Return the ad card wrapper, never a container holding several cards."""
    if link is None:
        return None
    node = link
    for _ in range(6):
        parent = getattr(node, "parent", None)
        if parent is None or not getattr(parent, "name", None):
            break
        classes = " ".join(parent.get("class") or [])
        if "adCard__card" in classes:
            return parent
        node = parent
    return getattr(link, "parent", None) or link


def _index_product(soup: BeautifulSoup) -> dict:
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "Product":
                return candidate
    return {}


def _index_detail_location(soup: BeautifulSoup) -> str:
    node = soup.select_one('[class*="sellerSection__bottomCard"]')
    if node is None:
        return ""
    text = " ".join(node.get_text(" ", strip=True).split())
    neighbourhood = node.find("b")
    if neighbourhood is not None:
        hood = " ".join(neighbourhood.get_text(" ", strip=True).split())
        rest = text.replace(hood, "", 1).strip(" ,")
        if hood and rest:
            return f"{rest}, {hood}"
        return hood or rest
    return text


def listing_from_index_detail(card: Card, html: str, watch_id: str, category: str) -> Listing:
    soup = BeautifulSoup(html, "lxml")
    product = _index_product(soup)
    offers = product.get("offers") if isinstance(product.get("offers"), dict) else {}

    root = soup.select_one('[class*="AdDetailsPage__content"]') or soup
    text = root.get_text("\n", strip=True)
    merged = f"{card.title}\n{card.snippet}\n{text}"
    year = _labeled_year(text) or _parse_year(merged)

    title = " ".join(str(product.get("name") or card.title).split())
    price: Optional[float] = None
    raw_price = offers.get("price")
    if isinstance(raw_price, (int, float)):
        price = float(raw_price)
    elif raw_price is not None:
        price = parse_price(str(raw_price))
    if price is None:
        price = card.price_eur if card.price_eur is not None else parse_price(text)

    location = _index_detail_location(soup)
    if not location:
        location = card.location.strip() if card.location else ""
    if not location or len(location) < 3:
        location = _guess_index_location(merged, title)

    description = str(product.get("description") or "").strip()
    if not description:
        # Keep enough detail text so location / novogradnja keywords reach the matcher.
        description = f"{card.snippet}\n{text}".strip()[:2000]

    images = product.get("image")
    image_url = card.image_url
    if isinstance(images, list) and images and isinstance(images[0], str):
        image_url = images[0]
    elif isinstance(images, str):
        image_url = images

    return Listing(
        id=f"index:{card.external_id}",
        source="index",
        watch_id=watch_id,
        title=title,
        url=card.url,
        price_eur=price,
        location=location,
        category=category,
        description=description,
        image_url=image_url,
        posted_at_millis=_posted_millis(soup),
        house_type=classify_house_type(text),
        rooms=parse_rooms(text),
        yard_m2=parse_square_meters(
            text,
            ("povrsina okucnice", "okucnica", "povrsina parcele", "parcela"),
        ),
        living_m2=parse_square_meters(
            text, ("stambena povrsina", "stambeni prostor", "povrsina stana")
        ),
        is_new_build=is_new_build(
            text, year, min_year=_build_year_min(watch_id)
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


def _labeled_year(text: str) -> Optional[int]:
    match = re.search(r"godina izgradnje\s*:?\s*((?:19|20)\d{2})", text.lower())
    return int(match.group(1)) if match else None


def _parse_year(text: str) -> Optional[int]:
    year = _labeled_year(text)
    if year is not None:
        return year
    match = re.search(r"\b(202[4-9]|2030)\b", text)
    return int(match.group(1)) if match else None
