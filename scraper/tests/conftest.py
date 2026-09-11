from __future__ import annotations

from realestate_monitor.models import Listing


def listing(
    *,
    listing_id: str = "njuskalo:1",
    source: str = "njuskalo",
    price_eur: float | None = 250_000.0,
    location: str = "Zagreb, Trešnjevka",
    title: str = "Kuća",
    description: str = "",
    house_type: str = "detached",
    rooms: float | None = None,
    living_m2: float | None = 120.0,
    yard_m2: float | None = None,
    is_new_build: bool = False,
    near_sea: bool = False,
) -> Listing:
    return Listing(
        id=listing_id,
        source=source,
        watch_id="zagreb_houses",
        title=title,
        url="https://example.test/listing",
        price_eur=price_eur,
        location=location,
        category="Kuće Zagreb",
        description=description,
        image_url=None,
        posted_at_millis=1,
        house_type=house_type,
        rooms=rooms,
        yard_m2=yard_m2,
        living_m2=living_m2,
        is_new_build=is_new_build,
        near_sea=near_sea,
    )
