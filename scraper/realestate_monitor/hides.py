from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Iterable

import httpx

from .store import Store

log = logging.getLogger(__name__)
NTFY_HIDE_BASE_URL = "https://ntfy.sh"


def iter_hide_messages(payload: str) -> Iterable[str]:
    for line in payload.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") != "message":
            continue
        listing_id = str(event.get("message") or "").strip()
        if listing_id:
            yield listing_id


def apply_remote_hides(store: Store) -> int:
    topic = os.getenv("NTFY_HIDE_TOPIC", "").strip()
    if not topic:
        return 0
    added = 0
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    try:
        response = httpx.get(
            f"{NTFY_HIDE_BASE_URL}/{topic}/json",
            params={"poll": "1"},
            timeout=20.0,
        )
        if response.status_code >= 400:
            log.warning("Hide inbox returned HTTP %s", response.status_code)
            return 0
        for listing_id in iter_hide_messages(response.text):
            if store.hide_listing(listing_id, now):
                added += 1
    except httpx.HTTPError:
        log.warning("Failed polling hide inbox")
    return added
