from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    return raw in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    discord_webhook_url: str
    poll_interval_sec: int
    api_host: str
    api_port: int
    headless: bool
    request_delay_sec: float
    max_pages: int

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def discord_enabled(self) -> bool:
        return bool(self.discord_webhook_url)


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "").strip(),
        poll_interval_sec=int(os.getenv("POLL_INTERVAL_SEC", "120")),
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8765")),
        headless=_flag("HEADLESS", True),
        request_delay_sec=float(os.getenv("REQUEST_DELAY_SEC", "2.0")),
        max_pages=int(os.getenv("MAX_PAGES", "3")),
    )
