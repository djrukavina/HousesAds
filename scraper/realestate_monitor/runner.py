from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit, urlparse

from .config import Settings
from .fetch import PageFetcher
from .models import Card, Listing
from .notify import send_alerts, send_text
from .parse import (
    listing_from_index_detail,
    listing_from_njuskalo_detail,
    parse_index_cards,
    parse_njuskalo_cards,
)
from .filters import prefilter_card
from .store import Store
from .watches import Watch, build_watches

log = logging.getLogger(__name__)


class Monitor:
    def __init__(self, settings: Settings, store: Store) -> None:
        self.settings = settings
        self.store = store
        self.fetcher = PageFetcher(settings)
        self.watches = build_watches()

    def close(self) -> None:
        self.fetcher.close()

    def run_cycle(self) -> int:
        first_run = self.store.is_empty()
        new_matches = 0
        for watch in self.watches:
            for url in watch.urls:
                new_matches += self._scrape_watch_url(watch, url, first_run)
        if first_run:
            total = len(self.store.all_listings())
            send_text(
                self.settings,
                f"Početna sinkronizacija gotova: {total} oglasa u bazi. Od sada šaljem samo nove.",
            )
        return new_matches

    def _scrape_watch_url(self, watch: Watch, url: str, first_run: bool) -> int:
        new_matches = 0
        is_index = "index.hr" in url
        # Njuškalo is fetched over plain HTTP with a mobile UA; Index needs a browser.
        force_browser = is_index
        wait_for_index_cards = is_index and "/oglas/" not in urlparse(url).path
        page_limit = watch.max_pages or self.settings.max_pages
        for page_number in range(1, page_limit + 1):
            page_url = _with_page(url, page_number)
            log.info("Fetching %s", page_url)
            try:
                html = self.fetcher.get(
                    page_url,
                    force_browser=force_browser,
                    wait_for_index_cards=wait_for_index_cards,
                )
            except Exception:
                log.exception("Failed fetching %s", page_url)
                break
            cards = parse_njuskalo_cards(html) if "njuskalo.hr" in url else parse_index_cards(html)
            log.info("Parsed %s cards from %s", len(cards), page_url)
            if not cards:
                break
            for card in cards:
                # Every watch URL is already scoped to one of WATCH_AREAS.
                if not prefilter_card(watch.id, card, url_scoped=True):
                    continue
                if self._handle_card(watch, card, first_run):
                    new_matches += 1
            if len(cards) < 8:
                break
        return new_matches

    def _handle_card(self, watch: Watch, card: Card, first_run: bool) -> bool:
        listing_id = f"{card.source}:{card.external_id}"
        already_seen = self.store.has_seen(listing_id)
        now = _now_millis()
        if self.store.is_hidden(listing_id):
            self.store.mark_seen(listing_id, now)
            return False
        if already_seen:
            return False
        try:
            listing = self._hydrate(watch, card)
        except Exception:
            log.exception("Detail parse failed for %s", card.url)
            self.store.mark_seen(listing_id, now)
            return False
        self.store.mark_seen(listing.id, now)
        if listing.posted_at_millis <= 0:
            listing.posted_at_millis = now
        if not watch.matcher(listing, True):
            return False
        listing.watch_id = watch.id
        listing.category = watch.category
        self.store.upsert_listing(listing)
        if not first_run:
            send_alerts(self.settings, listing)
            log.info("Alerted %s", listing.id)
        return True

    def _hydrate(self, watch: Watch, card: Card) -> Listing:
        is_index = card.source == "index"
        html = self.fetcher.get(
            card.url,
            force_browser=is_index,
            wait_for_index_cards=False,
        )
        if card.source == "njuskalo":
            return listing_from_njuskalo_detail(card, html, watch.id, watch.category)
        return listing_from_index_detail(card, html, watch.id, watch.category)


def run_forever(settings: Settings, store: Store) -> None:
    monitor = Monitor(settings, store)
    try:
        while True:
            started = time.time()
            try:
                found = monitor.run_cycle()
                log.info("Cycle finished, %s new matches", found)
            except Exception:
                log.exception("Cycle failed")
            elapsed = time.time() - started
            sleep_for = max(5, settings.poll_interval_sec - elapsed)
            time.sleep(sleep_for)
    finally:
        monitor.close()


def _with_page(url: str, page_number: int) -> str:
    if page_number <= 1:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    if "index.hr" in url:
        query["stranica"] = str(page_number)
    else:
        query["page"] = str(page_number)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _now_millis() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)
