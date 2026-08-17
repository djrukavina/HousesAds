from __future__ import annotations

import logging

import httpx

from .config import Settings
from .models import Listing

log = logging.getLogger(__name__)


def format_price_eur(price_eur: float | None) -> str:
    if price_eur is None:
        return "Po dogovoru"
    return f"{price_eur:,.0f} €".replace(",", ".")


def format_message(listing: Listing) -> str:
    price = format_price_eur(listing.price_eur)
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
    if settings.ntfy_enabled:
        _send_ntfy(settings, listing, text)
    if not settings.telegram_enabled and not settings.discord_enabled and not settings.ntfy_enabled:
        log.warning("No notifier configured; skipped alert for %s", listing.id)


def send_text(settings: Settings, text: str) -> None:
    if settings.telegram_enabled:
        _send_telegram(settings, text)
    if settings.discord_enabled:
        _send_discord(settings, text)
    if settings.ntfy_enabled:
        try:
            httpx.post(
                f"{settings.ntfy_server}/{settings.ntfy_topic}",
                content=text.encode("utf-8"),
                headers={"Title": "HousesAds"},
                timeout=20,
            )
        except Exception:
            log.exception("ntfy send failed")


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


def _send_ntfy(settings: Settings, listing: Listing, text: str) -> None:
    try:
        response = httpx.post(
            f"{settings.ntfy_server}/{settings.ntfy_topic}",
            content=text.encode("utf-8"),
            headers={
                "Title": f"Novi oglas: {listing.category}",
                "Click": listing.url,
                "Tags": "house",
                "Priority": "high",
            },
            timeout=20,
        )
        response.raise_for_status()
    except Exception:
        log.exception("ntfy send failed")
