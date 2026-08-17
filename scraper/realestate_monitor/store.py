from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from . import DB_PATH, HIDDEN_PATH, JSON_PATH
from .json_io import read_id_list, write_json
from .models import Listing


class Store:
    def __init__(self, path=DB_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS seen_ads (
                    id TEXT PRIMARY KEY,
                    first_seen_millis INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    watch_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    price_eur REAL,
                    location TEXT,
                    category TEXT,
                    description TEXT,
                    image_url TEXT,
                    posted_at_millis INTEGER,
                    house_type TEXT,
                    rooms REAL,
                    yard_m2 REAL,
                    living_m2 REAL,
                    is_new_build INTEGER,
                    near_sea INTEGER
                );
                CREATE TABLE IF NOT EXISTS hidden_ads (
                    id TEXT PRIMARY KEY,
                    hidden_at_millis INTEGER NOT NULL
                );
                """
            )
        self.import_hidden_json()

    def is_empty(self) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM seen_ads").fetchone()
            return int(row["n"]) == 0

    def has_seen(self, listing_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM seen_ads WHERE id = ?",
                (listing_id,),
            ).fetchone()
            return row is not None

    def mark_seen(self, listing_id: str, now_millis: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO seen_ads(id, first_seen_millis) VALUES(?, ?)",
                (listing_id, now_millis),
            )

    def is_hidden(self, listing_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM hidden_ads WHERE id = ?",
                (listing_id,),
            ).fetchone()
            return row is not None

    def hidden_ids(self) -> set[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id FROM hidden_ads").fetchall()
        return {str(row["id"]) for row in rows}

    def hide_listing(self, listing_id: str, now_millis: int | None = None) -> bool:
        listing_id = listing_id.strip()
        if not listing_id:
            return False
        hidden_at = now_millis or int(datetime.now(timezone.utc).timestamp() * 1000)
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO hidden_ads(id, hidden_at_millis) VALUES(?, ?)",
                (listing_id, hidden_at),
            )
            conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
            return cursor.rowcount > 0

    def import_hidden_json(self, path: Path | None = None) -> None:
        target = Path(path) if path is not None else HIDDEN_PATH
        for listing_id in read_id_list(target):
            self.hide_listing(listing_id, 0)

    def export_hidden_json(self, path: Path | None = None) -> Path:
        target = Path(path) if path is not None else HIDDEN_PATH
        write_json(target, {"ids": sorted(self.hidden_ids())})
        return target

    def upsert_listing(self, listing: Listing) -> None:
        if self.is_hidden(listing.id):
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO listings(
                    id, source, watch_id, title, url, price_eur, location, category,
                    description, image_url, posted_at_millis, house_type, rooms,
                    yard_m2, living_m2, is_new_build, near_sea
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    url=excluded.url,
                    price_eur=excluded.price_eur,
                    location=excluded.location,
                    category=excluded.category,
                    description=excluded.description,
                    image_url=excluded.image_url,
                    posted_at_millis=excluded.posted_at_millis,
                    house_type=excluded.house_type,
                    rooms=excluded.rooms,
                    yard_m2=excluded.yard_m2,
                    living_m2=excluded.living_m2,
                    is_new_build=excluded.is_new_build,
                    near_sea=excluded.near_sea
                """,
                (
                    listing.id,
                    listing.source,
                    listing.watch_id,
                    listing.title,
                    listing.url,
                    listing.price_eur,
                    listing.location,
                    listing.category,
                    listing.description,
                    listing.image_url,
                    listing.posted_at_millis,
                    listing.house_type,
                    listing.rooms,
                    listing.yard_m2,
                    listing.living_m2,
                    int(listing.is_new_build),
                    int(listing.near_sea),
                ),
            )

    def all_listings(self) -> list[Listing]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM listings
                WHERE id NOT IN (SELECT id FROM hidden_ads)
                ORDER BY posted_at_millis DESC, title ASC
                """
            ).fetchall()
        return [self._row_to_listing(row) for row in rows]

    def export_json(self, path: Path | None = None) -> Path:
        target = Path(path) if path is not None else JSON_PATH
        write_json(target, {"ads": [item.to_api() for item in self.all_listings()]})
        self.export_hidden_json()
        return target

    def _row_to_listing(self, row: sqlite3.Row) -> Listing:
        return Listing(
            id=row["id"],
            source=row["source"],
            watch_id=row["watch_id"],
            title=row["title"],
            url=row["url"],
            price_eur=row["price_eur"],
            location=row["location"] or "",
            category=row["category"] or "",
            description=row["description"] or "",
            image_url=row["image_url"],
            posted_at_millis=int(row["posted_at_millis"] or 0),
            house_type=row["house_type"] or "unknown",
            rooms=row["rooms"],
            yard_m2=row["yard_m2"],
            living_m2=row["living_m2"],
            is_new_build=bool(row["is_new_build"]),
            near_sea=bool(row["near_sea"]),
        )
