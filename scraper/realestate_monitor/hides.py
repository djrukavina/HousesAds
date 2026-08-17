from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import httpx

from .store import Store

log = logging.getLogger(__name__)


def apply_remote_hides(store: Store) -> int:
    topic = os.getenv("NTFY_HIDE_TOPIC", "").strip()
    if not topic:
        return 0
    added = 0
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    try:
        response = httpx.get(
            "https://ntfy.sh/" + topic + "/json",
            params={"poll": "1"},
            timeout=20.0,
        )
        if response.status_code >= 400:
            log.warning("Hide inbox returned HTTP %s", response.status_code)
            return 0
        for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("event") != "message":
                continue
            listing_id = str(payload.get("message") or "").strip()
            if listing_id and store.hide_listing(listing_id, now):
                added += 1
    except httpx.HTTPError:
        log.warning("Failed polling hide inbox")
    return added
