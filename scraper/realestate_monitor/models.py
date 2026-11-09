from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    id: str
    source: str
    watch_id: str
    title: str
    url: str
    price_eur: Optional[float]
    location: str
    category: str
    description: str
    image_url: Optional[str]
    posted_at_millis: int
    house_type: str = "unknown"
    rooms: Optional[float] = None
    yard_m2: Optional[float] = None
    living_m2: Optional[float] = None
    is_new_build: bool = False
    near_sea: bool = False
    build_year: Optional[int] = None

    def to_api(self) -> dict[str, object]:
        return {
            "id": self.id,
            "source": self.source,
            "watchId": self.watch_id,
            "title": self.title,
            "url": self.url,
            "priceEur": self.price_eur,
            "location": self.location,
            "category": self.category,
            "description": self.description,
            "imageUrl": self.image_url,
            "postedAtMillis": self.posted_at_millis,
            "houseType": self.house_type,
            "rooms": self.rooms,
            "yardM2": self.yard_m2,
            "livingM2": self.living_m2,
            "isNewBuild": self.is_new_build,
            "nearSea": self.near_sea,
        }


@dataclass
class Card:
    source: str
    external_id: str
    title: str
    url: str
    price_eur: Optional[float]
    location: str
    snippet: str
    image_url: Optional[str] = None
