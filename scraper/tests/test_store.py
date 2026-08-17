import json

from realestate_monitor.hides import iter_hide_messages
from realestate_monitor.json_io import read_id_list, write_json
from realestate_monitor.models import Listing
from realestate_monitor.store import Store
from tests.conftest import listing


def test_store_hides_and_exports_listing(tmp_path) -> None:
    db_path = tmp_path / "monitor.sqlite3"
    json_path = tmp_path / "listings.json"
    hidden_path = tmp_path / "hidden.json"
    store = Store(path=db_path)

    store.upsert_listing(listing(listing_id="njuskalo:1"))
    store.upsert_listing(listing(listing_id="njuskalo:2", title="Drugi oglas"))

    assert len(store.all_listings()) == 2

    store.hide_listing("njuskalo:1", now_millis=123)
    assert store.is_hidden("njuskalo:1")
    assert len(store.all_listings()) == 1

    store.export_json(path=json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert [item["id"] for item in payload["ads"]] == ["njuskalo:2"]

    write_json(hidden_path, {"ids": ["njuskalo:3"]})
    fresh = Store(path=tmp_path / "fresh.sqlite3")
    fresh.import_hidden_json(hidden_path)
    assert fresh.is_hidden("njuskalo:3")


def test_read_id_list_ignores_invalid_payload(tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not-json", encoding="utf-8")
    assert read_id_list(bad) == []


def test_iter_hide_messages_parses_ntfy_payload() -> None:
    payload = '\n'.join(
        [
            '{"event":"open","id":"1"}',
            '{"event":"message","message":"njuskalo:42"}',
            '{"event":"message","message":"  "}',
        ]
    )
    assert list(iter_hide_messages(payload)) == ["njuskalo:42"]
