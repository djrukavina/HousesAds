# HousesAds

Personal real-estate monitor for Croatian property listings. A Python scraper runs on GitHub Actions (no home PC required), publishes a shared JSON feed, and sends instant Telegram alerts. The **HousesAds** Android app reads that feed, caches listings locally, and notifies you when new matches appear.

## What it does

The system watches three custom search profiles and only stores ads that pass strict filters:

| Watch | Criteria |
|-------|----------|
| **Zagreb houses** | Zagreb area + Samobor, **€10,000–€300,000**, yard or living area ≥ 100 m², detached house **or** row house + new build. Sesvete and eastern districts (Dubrava, Peščenica, etc.) are excluded. |
| **Zagreb apartments** | Zagreb city, **€10,000–€300,000**, at least 3 rooms, living area ≥ 80 m², new build only. Eastern districts excluded. |
| **Coast houses** | Croatian islands, **€10,000–€50,000**, near the sea. |

Listing pages that require a browser are fetched with Playwright in CI.

## Architecture

```
GitHub Actions (scheduled)
        │
        ▼
  Python scraper ──► data/listings.json  ◄── Android app (Room cache)
        │                    │
        ├── monitor.sqlite3  │  GitHub raw URL
        ├── hidden.json      │
        └── Telegram alert   └── local notifications
```

- **`data/listings.json`** — feed the app downloads
- **`data/hidden.json`** — IDs you dismissed on the phone (synced via ntfy)
- **`data/monitor.sqlite3`** — scraper state so Telegram does not repeat old ads

Deleting an ad in the app hides it locally and publishes the ID to an ntfy topic; the next scrape cycle merges hides into `hidden.json` and removes them from the feed.

## Repository layout

```
├── app/                    # Android app (Jetpack Compose, Room, WorkManager)
├── scraper/                # Python monitor + pytest suite
│   └── realestate_monitor/ # fetch, parse, filters, store, watches
├── data/                   # Published listings (updated by CI)
└── .github/workflows/
    ├── scrape.yml          # Scheduled scraper + publish
    └── tests.yml           # Android unit tests + pytest
```

## Android app

- **Package:** `com.housesads`
- **Default feed:** `https://raw.githubusercontent.com/CurkovicDavid/HousesAds/main/data/listings.json`
- **Stack:** Jetpack Compose, Room, WorkManager background sync, Material 3
- **Features:** category tabs, favorites, open listing in browser, pull-to-refresh, system notifications for new ads

### Run locally

1. Open the project in Android Studio.
2. Connect a device or emulator (min SDK 24).
3. Run the **HousesAds** configuration (`com.housesads.MainActivity`).

If you previously installed the old **NjuskaloAds** app (`com.njuskalo.ads`), uninstall it first.

### Unit tests

```bash
./gradlew :app:testDebugUnitTest
```

## Scraper

### Run once locally (optional)

```bash
cd scraper
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env        # fill Telegram / ntfy secrets
python run_monitor.py --once
```

### Unit tests

```bash
cd scraper
pip install -r requirements.txt
python -m pytest -q
```

## GitHub Actions setup

Add these **repository secrets**:

| Secret | Purpose |
|--------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Your chat ID |
| `NTFY_HIDE_TOPIC` | Private ntfy topic for phone → repo hide sync |
| `NTFY_TOPIC` | Optional extra push channel |

## CI

- **Tests** — runs on every push to `main` (Kotlin unit tests + Python pytest)
- **Scrape listings** — hourly cron + manual dispatch; commits updated `data/` when listings change

## License

Private personal project. Listing content belongs to the original publishers; use responsibly and respect their terms of service.
