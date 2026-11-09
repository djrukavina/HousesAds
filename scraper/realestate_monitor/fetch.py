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

# ShieldSquare serves a CAPTCHA to desktop Chrome but the mobile pages are
# server-rendered and embed the full result set in window.__INITIAL_STATE__.
NJUSKALO_USER_AGENTS = (
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
        "Mobile/15E148 Safari/604.1"
    ),
    (
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 "
        "Mobile Safari/537.36"
    ),
)


def _headers(user_agent: str) -> dict[str, str]:
    return {
        "User-Agent": user_agent,
        "Accept-Language": "hr-HR,hr;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


class PageFetcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(
            headers=_headers(USER_AGENT),
            follow_redirects=True,
            timeout=30,
        )
        self._njuskalo_clients = [
            httpx.Client(
                headers=_headers(user_agent),
                follow_redirects=True,
                timeout=30,
            )
            for user_agent in NJUSKALO_USER_AGENTS
        ]
        self._playwright = None
        self._browser = None
        self._page = None

    def close(self) -> None:
        self._client.close()
        for client in self._njuskalo_clients:
            client.close()
        if self._page is not None:
            self._page.close()
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    def get(
        self,
        url: str,
        force_browser: bool = False,
        *,
        wait_for_index_cards: bool = False,
        wait_for_index_detail: bool = False,
    ) -> str:
        time.sleep(self.settings.request_delay_sec + random.uniform(0.2, 0.8))
        if "njuskalo.hr" in url:
            html = self._get_njuskalo(url)
            if html is not None:
                return html
            log.info("Njuškalo mobile fetch blocked for %s; falling back to browser", url)
            html = self._get_playwright(url, wait_for_index_cards=wait_for_index_cards)
            if "window.__INITIAL_STATE__" not in html:
                raise RuntimeError(f"Njuškalo blocked for {url}")
            return html
        elif not force_browser:
            try:
                response = self._client.get(url)
                html = response.text
                if response.status_code < 400 and not _looks_blocked(html):
                    return html
                log.info("HTTP fetch looked blocked for %s (%s)", url, response.status_code)
            except Exception:
                log.exception("HTTP fetch failed for %s", url)
        return self._get_playwright(
            url,
            wait_for_index_cards=wait_for_index_cards,
            wait_for_index_detail=wait_for_index_detail,
        )

    def _get_njuskalo(self, url: str) -> str | None:
        for attempt, client in enumerate(self._njuskalo_clients, start=1):
            try:
                response = client.get(url)
                html = response.text
                if (
                    response.status_code < 400
                    and not _looks_blocked(html)
                    and "window.__INITIAL_STATE__" in html
                ):
                    return html
                log.info(
                    "Njuškalo mobile attempt %s blocked for %s (%s)",
                    attempt,
                    url,
                    response.status_code,
                )
            except Exception:
                log.warning(
                    "Njuškalo mobile fetch failed for %s (attempt %s)",
                    url,
                    attempt,
                    exc_info=True,
                )
            time.sleep(1.0)
        return None

    def _get_playwright(
        self,
        url: str,
        *,
        wait_for_index_cards: bool = False,
        wait_for_index_detail: bool = False,
    ) -> str:
        page = self._ensure_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        if wait_for_index_cards:
            try:
                page.wait_for_selector('a[href*="/oglas/"]', timeout=20_000)
            except Exception:
                log.warning("Index cards did not render in time for %s", url)
        elif wait_for_index_detail:
            try:
                page.wait_for_selector(
                    '[class*="AdDetailsPage__content"]', timeout=20_000
                )
            except Exception:
                log.warning("Index detail did not render in time for %s", url)
            page.wait_for_timeout(500)
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
    # Normal Njuškalo pages also embed ShieldSquare/reCAPTCHA scripts, so only
    # match the actual interstitial page, not any mention of those vendors.
    blockers = (
        "<title>shieldsquare captcha",
        "validate.perfdrive.com",
        "access denied",
        "cf-challenge",
        "just a moment",
        "attention required! | cloudflare",
    )
    return any(token in lowered for token in blockers)
