from __future__ import annotations

import logging

import httpx

from .config import Settings
from .models import Listing

log = logging.getLogger(__name__)


def format_message(listing: Listing) -> str:
    price = "Po dogovoru" if listing.price_eur is None else f"{listing.price_eur:,.0f} €".replace(",", ".")
    return (
        f"Novi oglas: {listing.category}\n"
        f"{listing.title}\n"
        f"{price} · {listing.location}\n"
        f"{listing.url}"
    )


def send_alerts(settings: Settings, listing: Listing) -> None:
    text = format_message(listing)
    if settings.telegram_enabled:
        _send_telegram(settings, text)
    if settings.discord_enabled:
        _send_discord(settings, text)
    if not settings.telegram_enabled and not settings.discord_enabled:
        log.warning("No notifier configured; skipped alert for %s", listing.id)


def send_text(settings: Settings, text: str) -> None:
    if settings.telegram_enabled:
        _send_telegram(settings, text)
    if settings.discord_enabled:
        _send_discord(settings, text)


def _send_telegram(settings: Settings, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    try:
        response = httpx.post(url, json=payload, timeout=20)
        response.raise_for_status()
    except Exception:
        log.exception("Telegram send failed")


def _send_discord(settings: Settings, text: str) -> None:
    try:
        response = httpx.post(
            settings.discord_webhook_url,
            json={"content": text},
            timeout=20,
        )
        response.raise_for_status()
    except Exception:
        log.exception("Discord send failed")
