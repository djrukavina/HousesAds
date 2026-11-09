import json

from realestate_monitor.models import Card
from realestate_monitor.parse import (
    listing_from_index_detail,
    listing_from_njuskalo_detail,
    parse_index_cards,
    parse_njuskalo_cards,
)


def _state_html(store: str, page: dict) -> str:
    payload = {store: {"pageData": page}}
    return (
        "<html><script>window.__INITIAL_STATE__ = "
        f"{json.dumps(payload, ensure_ascii=False)};"
        "</script></html>"
    )


SAMPLE_NJUSKALO_HTML = """
<ul>
  <li class="EntityList-item">
    <article class="entity-body">
      <a href="/prodaja-stanova/zagreb/oglas-12345/stan">Trosoban stan Zagreb</a>
      <div class="entity-description-main">Lokacija: Zagreb, Trešnjevka</div>
      <strong class="price">289.000 €</strong>
    </article>
  </li>
</ul>
"""


def test_parse_njuskalo_cards_extracts_card() -> None:
    cards = parse_njuskalo_cards(SAMPLE_NJUSKALO_HTML)
    assert len(cards) == 1
    card = cards[0]
    assert card.external_id == "12345"
    assert card.price_eur == 289_000.0
    assert "Zagreb" in card.location


SAMPLE_INDEX_HTML = """
<html><body>
  <a href="/oglasi/nekretnine/prodaja-stanova/oglas/stan-zagreb-medvescak-70m2/7324120">
    Stan: Zagreb (Medveščak), 70m2 + 15m2 spremište (prodaja)
  </a>
  <div>17.08.2026. | 360.000 € | 3-SOBNI | Gornji Grad - Medveščak</div>
</body></html>
"""


def test_parse_index_cards_extracts_new_url_format() -> None:
    cards = parse_index_cards(SAMPLE_INDEX_HTML)
    assert len(cards) == 1
    card = cards[0]
    assert card.external_id == "7324120"
    assert card.source == "index"
    assert "Medveščak" in card.title
    assert card.url.endswith("/7324120")


def test_parse_index_cards_from_embedded_urls() -> None:
    html = (
        'script payload with '
        '"https://www.index.hr/oglasi/nekretnine/prodaja-kuca/oglas/kuca-zagreb/7497704"'
    )
    cards = parse_index_cards(html)
    assert len(cards) == 1
    assert cards[0].external_id == "7497704"


def _index_card_html(external_id: str, title: str, price: str, location: str, size: str = "") -> str:
    return f"""
    <div class="ant-col ant-col-xs-24">
      <a href="/oglasi/nekretnine/prodaja-kuca/oglas/kuca-{external_id}/{external_id}"
         title="{title}">
        <div class="adCard__card___vbwvv">
          <span>08.11.2026.</span>
          <span class="AdSummary__title___y1fZw">{title}</span>
          <span class="adPrice__price___3o3Dk">{price}</span>
          <span class="style__value___37YPR">{size}</span>
          <div class="adLocation__location___3r63d">{location}</div>
          <div style='background-image: url("https://img.index.hr/{external_id}.jpg");'></div>
        </div>
      </a>
    </div>
    """


def test_parse_index_cards_scopes_each_card_to_its_own_data() -> None:
    html = (
        "<html><body><div class='adList__row___2FDSq'>"
        + _index_card_html(
            "7041331",
            "Kuća Ivanić-Grad - Okolica (Lijevi Dubrovčak), 65m2, 4-sobna",
            "38.000 €",
            "Ivanić-Grad - Okolica",
            "65 M2",
        )
        + _index_card_html("7674840", "Kuća Bistra", "230.000 €", "Bistra", "150 M2")
        + "</div></body></html>"
    )
    cards = {card.external_id: card for card in parse_index_cards(html)}

    assert cards["7674840"].price_eur == 230_000.0
    assert cards["7674840"].location == "Bistra"
    assert cards["7674840"].title == "Kuća Bistra"
    assert cards["7674840"].image_url == "https://img.index.hr/7674840.jpg"
    assert cards["7041331"].price_eur == 38_000.0


def _index_detail_html() -> str:
    product = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Kuća Bistra (Bukovje Bistransko), 150m2, 3-sobna",
        "description": "Samostojeća kuća s velikom okućnicom.",
        "image": ["https://img.index.hr/detail.jpg"],
        "offers": {"@type": "Offer", "price": 230000, "priceCurrency": "EUR"},
    }
    return f"""
    <html><body>
      <div class="AdDetailsPage__content___3EBZJ">
        <h1 class="SummarySection__title___2rfVV">Kuća Bistra (Bukovje Bistransko), 150m2, 3-sobna</h1>
        <span class="SummarySection__price___1dmYQ">230.000 €</span>
        <section class="DetailSection__detailSection___3V1dL">
          <div>Karakteristike</div>
          <div>Godina izgradnje 1972</div>
          <div>Broj soba 3</div>
          <div>Stambena površina 150 m2</div>
          <div>Površina okućnice 550 m2</div>
          <div>Tip kuće Samostojeća</div>
        </section>
      </div>
      <div class="sellerSection__bottomCard___200Br">
        <b>Bukovje Bistransko</b> Bistra, Zagrebačka
      </div>
      <script type="application/ld+json">{json.dumps(product, ensure_ascii=False)}</script>
    </body></html>
    """


def test_listing_from_index_detail_reads_structured_data() -> None:
    card = Card(
        source="index",
        external_id="7674840",
        title="Kuća Bistra (Bukovje Bistransko), 150m2, 3-sobna",
        url="https://www.index.hr/oglasi/nekretnine/prodaja-kuca/oglas/kuca-bistra/7674840",
        price_eur=230_000.0,
        location="Bistra",
        snippet="",
    )
    listing = listing_from_index_detail(
        card, _index_detail_html(), "zagreb_houses", "Kuće"
    )

    assert listing.price_eur == 230_000.0
    assert listing.location == "Bistra, Zagrebačka, Bukovje Bistransko"
    assert listing.living_m2 == 150.0
    assert listing.yard_m2 == 550.0
    assert listing.rooms == 3.0
    assert listing.house_type == "detached"
    assert listing.is_new_build is False
    assert listing.image_url == "https://img.index.hr/detail.jpg"
    assert listing.description == "Samostojeća kuća s velikom okućnicom."


def test_parse_njuskalo_cards_reads_vue_state() -> None:
    page = {
        "regularListings": [
            {
                "id": "51820862",
                "title": "Kuća: Novi Zagreb (Donji Trpuci), 94.00 m2",
                "url": "/nekretnine/kuca-zagreb-donji-trpuci-94.00-m2-oglas-51820862",
                "priceFormatted": "154.000 €",
                "location": "Donji Trpuci - Brezovica",
                "abstracts": [
                    {"caption": "Lokacija", "value": "Donji Trpuci - Brezovica"}
                ],
                "highlights": [
                    {"label": "Stambena površina", "value": "94 m²"},
                    {"label": "Površina okućnice", "value": "Okućnica: 671 m²"},
                ],
                "image": "https://www.njuskalo.hr/image/51820862.jpg",
                "createdAt": "2026-11-08T14:33:55.000Z",
            }
        ],
        "promotedListings": [],
        "userPromotedListings": [],
        "superVauListings": [],
    }
    cards = parse_njuskalo_cards(_state_html("browseListingsStore", page))

    assert len(cards) == 1
    card = cards[0]
    assert card.source == "njuskalo"
    assert card.external_id == "51820862"
    assert card.price_eur == 154_000.0
    assert card.location == "Donji Trpuci - Brezovica"
    assert "Stambena površina: 94 m²" in card.snippet
    assert card.url.endswith("oglas-51820862")


def _njuskalo_detail_card() -> Card:
    return Card(
        source="njuskalo",
        external_id="51820862",
        title="Kuća: Novi Zagreb (Donji Trpuci), 94.00 m2",
        url="https://www.njuskalo.hr/nekretnine/kuca-zagreb-donji-trpuci-94.00-m2-oglas-51820862",
        price_eur=154_000.0,
        location="Donji Trpuci - Brezovica",
        snippet="Stambena površina: 94 m²",
    )


def test_listing_from_njuskalo_detail_reads_vue_state() -> None:
    page = {
        "listing": {
            "id": 51820862,
            "title": "Kuća: Novi Zagreb (Donji Trpuci), 94.00 m2 (prodaja)",
            "url": "/nekretnine/kuca-zagreb-donji-trpuci-94.00-m2-oglas-51820862",
            "price": 154000,
            "priceFormatted": "154.000 €",
            "createdAt": "2026-11-08T14:33:55.000Z",
            "image": "https://www.njuskalo.hr/image/51820862.jpg",
        },
        "boxes": {
            "basicDetailsBox": {
                "items": [
                    {
                        "label": "Lokacija",
                        "definition": "Grad Zagreb, Brezovica, Donji Trpuci",
                        "fieldName": "location",
                    },
                    {
                        "label": "Tip kuće",
                        "definition": "Samostojeća",
                        "fieldName": "houseBuildingType",
                    },
                    {
                        "label": "Broj soba",
                        "definition": "3",
                        "fieldName": "numberOfRooms",
                    },
                    {
                        "label": "Stambena površina",
                        "definition": "94,00 m²",
                        "fieldName": "livingArea",
                    },
                    {
                        "label": "Površina okućnice",
                        "definition": "671,00 m²",
                        "fieldName": "yardArea",
                    },
                    {
                        "label": "Godina izgradnje",
                        "definition": "1950.",
                        "fieldName": "yearOfConstruction",
                    },
                ]
            },
            "detailDescriptionBox": {"text": "Samostojeća kuća s velikom okućnicom."},
            "additionalDetailsBox": {
                "items": [
                    {"type": "key-value", "key": "Podaci o objektu", "values": ["Gradski plin"]}
                ]
            },
        },
        "media": {
            "photos": [{"previewUrl": "https://www.njuskalo.hr/image-big/51820862.jpg"}]
        },
    }
    html = _state_html("listingDetailStore", page)

    listing = listing_from_njuskalo_detail(
        _njuskalo_detail_card(), html, "zagreb_houses", "Kuće"
    )

    assert listing.id == "njuskalo:51820862"
    assert listing.price_eur == 154_000.0
    assert listing.location == "Grad Zagreb, Brezovica, Donji Trpuci"
    assert listing.living_m2 == 94.0
    assert listing.yard_m2 == 671.0
    assert listing.rooms == 3.0
    assert listing.house_type == "detached"
    assert listing.image_url == "https://www.njuskalo.hr/image-big/51820862.jpg"
    assert listing.posted_at_millis > 0
    # 1950 is the labelled build year; the 2026 date must not be treated as one.
    assert listing.is_new_build is False


def test_listing_from_njuskalo_detail_parses_croatian_area_format() -> None:
    page = {
        "listing": {"id": 52183664, "title": "Kuća Brezovica"},
        "boxes": {
            "basicDetailsBox": {
                "items": [
                    {
                        "label": "Stambena površina",
                        "definition": "94,50 m²",
                        "fieldName": "livingArea",
                    },
                    {
                        "label": "Površina okućnice",
                        "definition": "1.424,00 m²",
                        "fieldName": "yardArea",
                    },
                ]
            }
        },
    }
    card = Card(
        source="njuskalo",
        external_id="52183664",
        title="Kuća Brezovica",
        url="https://www.njuskalo.hr/nekretnine/kuca-oglas-52183664",
        price_eur=75_000.0,
        location="",
        snippet="",
    )

    listing = listing_from_njuskalo_detail(
        card, _state_html("listingDetailStore", page), "zagreb_houses", "Kuće"
    )

    assert listing.living_m2 == 94.5
    assert listing.yard_m2 == 1424.0


def test_listing_from_njuskalo_detail_reads_novogradnja() -> None:
    page = {
        "listing": {
            "id": 51755606,
            "title": "JARUNSKI VRTOVI – trosoban stan 75 m2",
            "url": "/nekretnine/jarunski-vrtovi-oglas-51755606",
            "price": 543384,
            "priceFormatted": "543.384 €",
            "createdAt": "2026-11-09T19:28:14.000Z",
        },
        "boxes": {
            "basicDetailsBox": {
                "items": [
                    {
                        "label": "Lokacija",
                        "definition": "Grad Zagreb, Trešnjevka - Jug, Jarun",
                        "fieldName": "location",
                    },
                    {
                        "label": "Broj soba",
                        "definition": "3-sobni",
                        "fieldName": "numberOfRooms",
                    },
                    {
                        "label": "Stambena površina",
                        "definition": "75,47 m²",
                        "fieldName": "livingArea",
                    },
                    {
                        "label": "Godina izgradnje",
                        "definition": "2005.",
                        "fieldName": "yearOfConstruction",
                    },
                ]
            },
            "detailDescriptionBox": {"text": "Novi stambeni kompleks uz jezero Jarun."},
            "additionalDetailsBox": {
                "items": [
                    {
                        "type": "key-value",
                        "key": "Podaci o objektu",
                        "values": ["Novogradnja", "Gradski plin"],
                    }
                ]
            },
        },
    }
    card = Card(
        source="njuskalo",
        external_id="51755606",
        title="JARUNSKI VRTOVI – trosoban stan 75 m2",
        url="https://www.njuskalo.hr/nekretnine/jarunski-vrtovi-oglas-51755606",
        price_eur=543_384.0,
        location="",
        snippet="",
    )

    listing = listing_from_njuskalo_detail(
        card, _state_html("listingDetailStore", page), "zagreb_apartments", "Stanovi"
    )

    assert listing.living_m2 == 75.47
    assert listing.price_eur == 543_384.0
    assert listing.rooms == 3.0
    assert listing.is_new_build is True
