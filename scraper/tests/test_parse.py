from realestate_monitor.parse import parse_index_cards, parse_njuskalo_cards


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
