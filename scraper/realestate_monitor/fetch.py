from __future__ import annotations

import logging
import random
import time

import httpx

from .config import Settings

log = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class PageFetcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "hr-HR,hr;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=30,
        )
        self._playwright = None
        self._browser = None
        self._page = None

    def close(self) -> None:
        self._client.close()
        if self._page is not None:
            self._page.close()
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    def get(self, url: str, force_browser: bool = False, *, wait_for_index_cards: bool = False) -> str:
        time.sleep(self.settings.request_delay_sec + random.uniform(0.2, 0.8))
        if not force_browser:
            try:
                response = self._client.get(url)
                html = response.text
                if response.status_code < 400 and not _looks_blocked(html):
                    return html
                log.info("HTTP fetch looked blocked for %s (%s)", url, response.status_code)
            except Exception:
                log.exception("HTTP fetch failed for %s", url)
        return self._get_playwright(url, wait_for_index_cards=wait_for_index_cards)

    def _get_playwright(self, url: str, *, wait_for_index_cards: bool = False) -> str:
        page = self._ensure_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        if wait_for_index_cards:
            try:
                page.wait_for_selector('a[href*="/oglas/"]', timeout=20_000)
            except Exception:
                log.warning("Index cards did not render in time for %s", url)
        else:
            page.wait_for_timeout(1500)
        return page.content()

    def _ensure_page(self):
        if self._page is not None:
            return self._page
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.settings.headless)
        context = self._browser.new_context(
            locale="hr-HR",
            user_agent=USER_AGENT,
        )
        self._page = context.new_page()
        return self._page


def _looks_blocked(html: str) -> bool:
    lowered = html.lower()
    if len(html) < 1500:
        return True
    blockers = ("captcha", "access denied", "cf-challenge", "just a moment")
    return any(token in lowered for token in blockers)
