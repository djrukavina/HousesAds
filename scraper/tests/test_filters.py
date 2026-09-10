from realestate_monitor.filters import (
    card_price_ok,
    is_croatian_island,
    is_excluded_zagreb_area,
    matches_coast_house,
    matches_zagreb_apartment,
    matches_zagreb_house,
    parse_price,
    parse_rooms,
    prefilter_card,
)
from realestate_monitor.models import Card
from tests.conftest import listing


def test_parse_price_reads_euro_amount() -> None:
    assert parse_price("Cijena: 289.000 €") == 289_000.0


def test_parse_rooms_detects_trosoban() -> None:
    assert parse_rooms("Trosoban stan, novogradnja") == 3.0


def test_matches_zagreb_house_for_detached_listing() -> None:
    assert matches_zagreb_house(
        listing(location="Samobor", living_m2=110.0, house_type="detached")
    )


def test_rejects_zagreb_house_in_sesvete() -> None:
    assert not matches_zagreb_house(
        listing(
            location="Zagreb, Sesvete, Markovo Polje",
            living_m2=120.0,
            house_type="detached",
        )
    )


def test_rejects_zagreb_house_in_dubrava() -> None:
    assert not matches_zagreb_house(
        listing(
            title="Obiteljska kuća",
            location="Zagreb, Gornja Dubrava",
            living_m2=150.0,
            house_type="detached",
        )
    )


def test_rejects_zagreb_apartment_in_sesvete() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Sesvete, Gajišće",
            description="Novogradnja, stambena povrsina 72 m2",
            rooms=3.0,
            living_m2=72.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_in_pescenica() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Peščenica",
            description="Novogradnja, stambena povrsina 85 m2",
            rooms=3.0,
            living_m2=85.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_in_velika_gorica() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Velika Gorica",
            description="Novogradnja, stambena povrsina 72 m2",
            rooms=3.0,
            living_m2=72.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_matches_zagreb_apartment_in_county_town() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zaprešić",
            description="Novogradnja, stambena povrsina 72 m2",
            rooms=3.0,
            living_m2=72.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_matches_zagreb_apartment_at_70m2() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka",
            description="Novogradnja, stambena povrsina 70 m2",
            rooms=3.0,
            living_m2=70.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_below_70m2() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka",
            description="Novogradnja, stambena povrsina 69 m2",
            rooms=3.0,
            living_m2=69.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_is_excluded_zagreb_area_detects_eastern_districts() -> None:
    assert is_excluded_zagreb_area("Zagreb, Sesvete")
    assert is_excluded_zagreb_area("Velika Gorica")
    assert is_excluded_zagreb_area("Stan: Zagreb, Dubrava")
    assert not is_excluded_zagreb_area("Zagreb, Trešnjevka")


def test_island_ist_does_not_match_istra() -> None:
    assert not is_croatian_island("Kuća u Istri, Opatija")
    assert is_croatian_island("Kuća na otoku Ist")


def test_card_price_ok_for_each_watch() -> None:
    assert card_price_ok("zagreb_houses", 250_000.0)
    assert not card_price_ok("zagreb_houses", 5_000.0)
    assert card_price_ok("zagreb_apartments", 340_000.0)
    assert not card_price_ok("zagreb_apartments", 341_000.0)
    assert card_price_ok("coast_houses", 25_000.0)
    assert not card_price_ok("coast_houses", None)


def test_prefilter_card_rejects_cheap_coast_listing() -> None:
    card = Card(
        source="index",
        external_id="1",
        title="Kuća Krk",
        url="https://www.index.hr/oglasi/krk",
        price_eur=3_000.0,
        location="Krk",
        snippet="uz more",
    )
    assert not prefilter_card("coast_houses", card)


def test_prefilter_allows_index_zagreb_card_without_location_text() -> None:
    card = Card(
        source="index",
        external_id="2",
        title="Lijepa obiteljska kuca",
        url="https://www.index.hr/oglasi/nekretnine/prodaja-kuca/oglas/lijepa/123",
        price_eur=180_000.0,
        location="",
        snippet="opis bez grada",
    )
    assert prefilter_card("zagreb_houses", card)


def test_prefilter_allows_index_coast_card_without_price() -> None:
    card = Card(
        source="index",
        external_id="3",
        title="Kuca uz more",
        url="https://www.index.hr/oglasi/nekretnine/prodaja-kuca/oglas/kuca/456",
        price_eur=None,
        location="",
        snippet="kratki opis",
    )
    assert prefilter_card("coast_houses", card)


def test_prefilter_still_requires_location_for_njuskalo_zagreb() -> None:
    card = Card(
        source="njuskalo",
        external_id="4",
        title="Kuca bez lokacije",
        url="https://www.njuskalo.hr/nekretnine/123",
        price_eur=180_000.0,
        location="",
        snippet="bez grada",
    )
    assert not prefilter_card("zagreb_houses", card)


def test_rejects_zagreb_house_above_budget() -> None:
    assert not matches_zagreb_house(listing(price_eur=350_000.0))


def test_rejects_zagreb_house_below_min_price() -> None:
    assert not matches_zagreb_house(
        listing(price_eur=5_000.0, living_m2=120.0, house_type="detached")
    )


def test_rejects_zagreb_apartment_below_min_price() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            price_eur=8_000.0,
            description="Novogradnja, stambena povrsina 82 m2",
            rooms=3.0,
            living_m2=82.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_matches_zagreb_apartment_at_340k() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka",
            price_eur=340_000.0,
            description="Novogradnja, stambena povrsina 80 m2",
            rooms=3.0,
            living_m2=80.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_above_340k() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka",
            price_eur=341_000.0,
            description="Novogradnja, stambena povrsina 80 m2",
            rooms=3.0,
            living_m2=80.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_matches_zagreb_apartment_with_all_required_fields() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            description="Novogradnja, stambena povrsina 82 m2",
            rooms=3.0,
            living_m2=82.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_without_new_build() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            rooms=3.0,
            living_m2=90.0,
            is_new_build=False,
            description="Stari stan",
        )
    )


def test_matches_coast_house_near_sea() -> None:
    assert matches_coast_house(
        listing(
            price_eur=45_000.0,
            location="Krk",
            description="Kuća uz more",
            living_m2=60.0,
            near_sea=True,
        )
    )


def test_rejects_coast_house_below_min_price() -> None:
    assert not matches_coast_house(
        listing(
            price_eur=5_000.0,
            location="Krk",
            description="Kuća uz more",
            living_m2=60.0,
            near_sea=True,
        )
    )


def test_rejects_coast_house_istra_false_island() -> None:
    assert not matches_coast_house(
        listing(
            price_eur=40_000.0,
            location="Istra, Opatija",
            description="Kuća uz more",
            living_m2=60.0,
            near_sea=True,
        )
    )
