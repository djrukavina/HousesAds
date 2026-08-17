from realestate_monitor.filters import (
    is_excluded_zagreb_area,
    matches_coast_house,
    matches_zagreb_apartment,
    matches_zagreb_house,
    parse_price,
    parse_rooms,
)
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
            description="Novogradnja, stambena povrsina 82 m2",
            rooms=3.0,
            living_m2=82.0,
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


def test_is_excluded_zagreb_area_detects_eastern_districts() -> None:
    assert is_excluded_zagreb_area("Zagreb, Sesvete")
    assert is_excluded_zagreb_area("Stan: Zagreb, Dubrava")
    assert not is_excluded_zagreb_area("Zagreb, Trešnjevka")


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
