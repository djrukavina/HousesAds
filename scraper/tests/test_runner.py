from realestate_monitor.config import Settings
from realestate_monitor.models import Card
from realestate_monitor.runner import Monitor
from realestate_monitor.store import Store
from realestate_monitor.watches import build_watches


class _FailingFetcher:
    def get(self, *_args, **_kwargs):
        raise RuntimeError("blocked")

    def close(self) -> None:
        pass


def _settings() -> Settings:
    return Settings(
        telegram_bot_token="",
        telegram_chat_id="",
        discord_webhook_url="",
        ntfy_server="https://ntfy.sh",
        ntfy_topic="",
        poll_interval_sec=1,
        headless=True,
        request_delay_sec=0.0,
        max_pages=1,
    )


def test_failed_detail_is_retried_next_cycle(tmp_path) -> None:
    store = Store(tmp_path / "monitor.sqlite3")
    monitor = Monitor(_settings(), store)
    monitor.fetcher.close()
    monitor.fetcher = _FailingFetcher()
    watch = build_watches()[0]
    card = Card(
        source="njuskalo",
        external_id="123",
        title="Kuća Brezovica",
        url="https://www.njuskalo.hr/nekretnine/kuca-oglas-123",
        price_eur=150_000.0,
        location="Brezovica",
        snippet="",
    )

    try:
        assert monitor._handle_card(watch, card, first_run=False) is False
        assert not store.has_seen("njuskalo:123")
    finally:
        monitor.close()
