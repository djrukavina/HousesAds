from realestate_monitor.constants import (
    MIN_ZAGREB_APARTMENT_BUILD_YEAR,
    MIN_ZAGREB_HOUSE_BUILD_YEAR,
)
from realestate_monitor.filters import (
    card_price_ok,
    is_croatian_island,
    is_new_build,
    is_watched_area,
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


def test_new_build_uses_watch_specific_year() -> None:
    assert is_new_build("", 2000, min_year=MIN_ZAGREB_HOUSE_BUILD_YEAR)
    assert not is_new_build("", 1999, min_year=MIN_ZAGREB_HOUSE_BUILD_YEAR)
    assert is_new_build("", 2010, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR)
    assert not is_new_build("", 2009, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR)
    assert not is_new_build("", None, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR)
    assert is_new_build("novogradnja", 1990, min_year=MIN_ZAGREB_APARTMENT_BUILD_YEAR)


def test_matches_zagreb_house_for_detached_listing() -> None:
    assert matches_zagreb_house(
        listing(
            location="Zaprešić",
            living_m2=110.0,
            house_type="detached",
            is_new_build=True,
        )
    )


def test_matches_zagreb_house_in_sesvete() -> None:
    assert matches_zagreb_house(
        listing(
            location="Zagreb, Sesvete, Markovo Polje",
            living_m2=120.0,
            house_type="detached",
            is_new_build=True,
        )
    )


def test_rejects_zagreb_house_built_before_2000() -> None:
    assert not matches_zagreb_house(
        listing(
            location="Zaprešić",
            living_m2=120.0,
            house_type="detached",
            is_new_build=False,
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


def test_matches_zagreb_apartment_in_sesvete() -> None:
    assert matches_zagreb_apartment(
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


def test_matches_zagreb_apartment_in_velika_gorica() -> None:
    assert matches_zagreb_apartment(
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


def test_matches_zagreb_apartment_at_55m2() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka - Jug",
            description="Novogradnja, stambena povrsina 55 m2",
            rooms=3.0,
            living_m2=55.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_below_55m2() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka - Jug",
            description="Novogradnja, stambena povrsina 54 m2",
            rooms=3.0,
            living_m2=54.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_is_watched_area_accepts_configured_areas() -> None:
    assert is_watched_area("Zagreb, Novi Zagreb - Istok")
    assert is_watched_area("Zagreb, Novi Zagreb - Zapad")
    assert is_watched_area("Zagreb, Podsused - Vrapče")
    assert is_watched_area("Brestje - Sesvete")
    assert is_watched_area("Zagreb, Stenjevec")
    assert is_watched_area("Zagreb, Trešnjevka - Jug")
    assert is_watched_area("Zagreb - Okolica")
    assert is_watched_area("Dugo Selo - Okolica")
    assert is_watched_area("Ivanić-Grad")
    assert is_watched_area("Velika Gorica - Okolica")
    assert is_watched_area("Zaprešić")
    assert is_watched_area("Donja Bistra")
    assert is_watched_area("Kloštar Ivanić")
    assert is_watched_area("Rugvica")
    assert is_watched_area("Stupnik")


def test_is_watched_area_rejects_other_locations() -> None:
    assert not is_watched_area("Zagreb, Maksimir")
    assert not is_watched_area("Zagreb, Donji Grad")
    assert not is_watched_area("Zagreb, Trešnjevka - Sjever")
    assert not is_watched_area("Samobor")
    assert not is_watched_area("Jastrebarsko")
    assert not is_watched_area("Sveta Nedelja")
    assert not is_watched_area("Split")


def test_island_ist_does_not_match_istra() -> None:
    assert not is_croatian_island("Kuća u Istri, Opatija")
    assert is_croatian_island("Kuća na otoku Ist")


def test_card_price_ok_for_each_watch() -> None:
    assert card_price_ok("zagreb_houses", 240_000.0)
    assert not card_price_ok("zagreb_houses", 241_000.0)
    assert not card_price_ok("zagreb_houses", 5_000.0)
    assert card_price_ok("zagreb_apartments", 300_000.0)
    assert not card_price_ok("zagreb_apartments", 301_000.0)
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


def test_accepts_neighbourhood_location_when_url_scoped() -> None:
    # Njuškalo often names only the neighbourhood; the per-area URL is authoritative.
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb (Blato)",
            description="Novogradnja, stambena povrsina 82 m2",
            rooms=3.0,
            living_m2=82.0,
            is_new_build=True,
            house_type="unknown",
        ),
        url_scoped=True,
    )


def test_prefilter_skips_location_when_url_scoped() -> None:
    card = Card(
        source="njuskalo",
        external_id="5",
        title="Stan: Zagreb (Blato), 82 m2, novogradnja",
        url="https://www.njuskalo.hr/prodaja-stanova/novi-zagreb-istok/oglas-5",
        price_eur=220_000.0,
        location="",
        snippet="Zagreb (Blato)",
    )
    assert not prefilter_card("zagreb_apartments", card)
    assert prefilter_card("zagreb_apartments", card, url_scoped=True)


def test_matches_zagreb_house_at_240k() -> None:
    assert matches_zagreb_house(
        listing(
            price_eur=240_000.0,
            living_m2=90.0,
            house_type="detached",
            is_new_build=True,
        )
    )


def test_rejects_zagreb_house_above_budget() -> None:
    assert not matches_zagreb_house(
        listing(price_eur=241_000.0, living_m2=90.0, house_type="detached")
    )


def test_matches_zagreb_house_at_90m2() -> None:
    assert matches_zagreb_house(
        listing(living_m2=90.0, house_type="detached", is_new_build=True)
    )


def test_rejects_zagreb_house_below_90m2() -> None:
    assert not matches_zagreb_house(
        listing(living_m2=89.0, yard_m2=None, house_type="detached")
    )


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


def test_matches_zagreb_apartment_at_300k() -> None:
    assert matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka - Jug",
            price_eur=300_000.0,
            description="Novogradnja, stambena povrsina 80 m2",
            rooms=3.0,
            living_m2=80.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_rejects_zagreb_apartment_above_300k() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Zagreb, Trešnjevka - Jug",
            price_eur=301_000.0,
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


def test_index_apartment_allows_missing_rooms_size_and_new_build() -> None:
    assert matches_zagreb_apartment(
        listing(
            listing_id="index:1",
            source="index",
            title="Stan Zagreb",
            location="Zagreb",
            rooms=None,
            living_m2=None,
            is_new_build=False,
            description="Stan u Zagrebu",
            house_type="unknown",
        )
    )


def test_rejects_njuskalo_apartment_outside_watched_area() -> None:
    assert not matches_zagreb_apartment(
        listing(
            title="Trosoban stan",
            location="Samobor",
            description="Novogradnja, stambena povrsina 82 m2",
            rooms=3.0,
            living_m2=82.0,
            is_new_build=True,
            house_type="unknown",
        )
    )


def test_index_house_allows_unknown_type_without_size() -> None:
    assert matches_zagreb_house(
        listing(
            listing_id="index:3",
            source="index",
            title="Kuća Zagreb",
            location="Zagreb",
            living_m2=None,
            yard_m2=None,
            house_type="unknown",
            description="Kuća u Zagrebu",
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


def _njuskalo_card(*, price: float, title: str, snippet: str, location: str = "") -> Card:
    return Card(
        source="njuskalo",
        external_id="9",
        title=title,
        url="https://www.njuskalo.hr/prodaja-stanova/tresnjevka-jug/oglas-9",
        price_eur=price,
        location=location,
        snippet=snippet,
    )


def test_prefilter_njuskalo_apartment_rejects_small_flat() -> None:
    card = _njuskalo_card(
        price=199_000.0,
        title="Stan: Zagreb (Prečko), 48.00 m2",
        snippet="Stambena površina: 48 m² | Godina izgradnje: 1968",
    )
    assert not prefilter_card("zagreb_apartments", card, url_scoped=True)


def test_prefilter_njuskalo_apartment_rejects_old_build() -> None:
    card = _njuskalo_card(
        price=220_000.0,
        title="Stan: Zagreb (Blato), 70 m2",
        snippet="Stambena površina: 70 m² | Godina izgradnje: 2005",
    )
    assert not prefilter_card("zagreb_apartments", card, url_scoped=True)


def test_prefilter_njuskalo_apartment_keeps_novogradnja() -> None:
    card = _njuskalo_card(
        price=220_000.0,
        title="Stan: Zagreb (Blato), 70 m2",
        snippet="Stambena površina: 70 m² | Godina izgradnje: 2005 | Novogradnja: Novogradnja",
    )
    assert prefilter_card("zagreb_apartments", card, url_scoped=True)


def test_prefilter_njuskalo_apartment_keeps_card_without_size() -> None:
    card = _njuskalo_card(
        price=220_000.0,
        title="Stan: Zagreb (Blato)",
        snippet="Lokacija: Zagreb (Blato)",
    )
    assert prefilter_card("zagreb_apartments", card, url_scoped=True)


def test_prefilter_njuskalo_house_rejects_small_and_old() -> None:
    card = _njuskalo_card(
        price=105_000.0,
        title="ZGB-BREZOVICA: Prodaje se starinska kućica",
        snippet=(
            "Tip kuće: Samostojeća | Stambena površina: 49 m² | "
            "Površina okućnice: 317 m² | Godina izgradnje: 1950"
        ),
    )
    assert not prefilter_card("zagreb_houses", card, url_scoped=True)


def test_prefilter_njuskalo_house_rejects_small_living_and_yard() -> None:
    card = _njuskalo_card(
        price=120_000.0,
        title="Kuća Brezovica",
        snippet=(
            "Tip kuće: Samostojeća | Stambena površina: 49 m² | "
            "Površina okućnice: 40 m² | Godina izgradnje: 2015"
        ),
    )
    assert not prefilter_card("zagreb_houses", card, url_scoped=True)


def test_prefilter_njuskalo_house_keeps_large_yard() -> None:
    card = _njuskalo_card(
        price=120_000.0,
        title="Kuća Brezovica",
        snippet=(
            "Tip kuće: Samostojeća | Stambena površina: 49 m² | "
            "Površina okućnice: 317 m² | Godina izgradnje: 2015"
        ),
    )
    assert prefilter_card("zagreb_houses", card, url_scoped=True)


def test_prefilter_njuskalo_house_rejects_duplex() -> None:
    card = _njuskalo_card(
        price=180_000.0,
        title="Dvojna kuća Brezovica",
        snippet=(
            "Tip kuće: Dvojna kuća | Stambena površina: 120 m² | "
            "Površina okućnice: 150 m² | Godina izgradnje: 2015"
        ),
    )
    assert not prefilter_card("zagreb_houses", card, url_scoped=True)


def test_prefilter_njuskalo_house_keeps_card_without_year_or_size() -> None:
    card = _njuskalo_card(
        price=180_000.0,
        title="Kuća Brezovica",
        snippet="Lokacija: Brezovica",
    )
    assert prefilter_card("zagreb_houses", card, url_scoped=True)
