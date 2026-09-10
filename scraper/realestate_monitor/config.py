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
    ntfy_server: str
    ntfy_topic: str
    poll_interval_sec: int
    headless: bool
    request_delay_sec: float
    max_pages: int

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def discord_enabled(self) -> bool:
        return bool(self.discord_webhook_url)

    @property
    def ntfy_enabled(self) -> bool:
        return bool(self.ntfy_topic)


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "").strip(),
        ntfy_server=os.getenv("NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/"),
        ntfy_topic=os.getenv("NTFY_TOPIC", "").strip(),
        poll_interval_sec=int(os.getenv("POLL_INTERVAL_SEC", "30")),
        headless=_flag("HEADLESS", True),
        request_delay_sec=float(os.getenv("REQUEST_DELAY_SEC", "1.0")),
        max_pages=int(os.getenv("MAX_PAGES", "1")),
    )
