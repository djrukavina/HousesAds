# HousesAds

Personal real-estate monitor for Croatian property listings. A Python scraper runs on GitHub Actions (no home PC required), publishes a shared JSON feed, and sends instant Telegram alerts. The **HousesAds** Android app reads that feed and caches listings locally for browsing.

## What it does

The system watches two custom search profiles and only stores ads that pass strict filters:

| Watch | Criteria |
|-------|----------|
| **Houses** | The configured Zagreb/Zagrebačka areas, **€10,000–€240,000**, yard or living area ≥ **90 m²**, detached house **or** row house, built **2000 or later**. |
| **Apartments** | The configured Zagreb/Zagrebačka areas, **€10,000–€300,000**, living area ≥ **55 m²**, built **2010 or later**. |

The watched areas are defined once in `scraper/realestate_monitor/constants.py` (`WATCH_AREAS`) and used for both portals. Grad Zagreb: Brezovica, Novi Zagreb - Istok, Novi Zagreb - Zapad, Podsused - Vrapče, Sesvete, Stenjevec, Trešnjevka - Jug, Zagreb - Okolica. Zagrebačka županija: Dugo Selo, Ivanić-Grad, Velika Gorica, Zaprešić, Bistra, Kloštar Ivanić, Rugvica, Stupnik, plus Dugo Selo - Okolica, Ivanić-Grad - Okolica and Velika Gorica - Okolica.

Each watch scrapes one Njuškalo search URL per area plus a single Index search. The search URL defines the area, so location text on Njuškalo ads is not used to reject them — it often names only a neighbourhood (e.g. `Zagreb (Blato)`).

**Njuškalo scrape:** desktop and headless requests hit a ShieldSquare CAPTCHA. The scraper therefore requests Njuškalo with an iPhone/Android user agent over plain HTTP; those pages are server-rendered and embed all list and detail data in `window.__INITIAL_STATE__`, which is parsed directly (no browser needed). Playwright is only used for Index. Njuškalo cards are prefiltered conservatively — only when the card text already proves a size/year/type mismatch — so unclear ads are still hydrated from the detail page.

**Index scrape:** Index ignores location and price in the URL path and in plain query params; it only honours the `searchQuery` JSON. The scraper therefore sends `includeCityIds` (all watched areas), `priceFrom` and `priceTo` inside a twice-encoded `searchQuery`. Sparse Index list cards often omit location/price text, so Index cards skip the location *card* prefilter and are hydrated from the detail page before the full matcher runs. Matchers are slightly softer for Index (missing m²/house-type/build-year text does not auto-reject).

## Architecture

```
GitHub Actions (scheduled)
        │
        ▼
  Python scraper ──► data/listings.json  ◄── Android app (Room cache)
        │                    │
        ├── monitor.sqlite3  │  GitHub raw URL
        ├── hidden.json      │
        └── Telegram alert   └── (browse in app)
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
- **Default feed:** `https://raw.githubusercontent.com/djrukavina/HousesAds/main/data/listings.json`
- **Stack:** Jetpack Compose, Room, WorkManager background sync, Material 3
- **Features:** category tabs, favorites, open listing in browser, pull-to-refresh, background sync
- **Alerts:** handled exclusively by Telegram (no duplicate phone notifications)

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

Runs on GitHub Actions every 2 hours (`--once`), writes `data/listings.json`, and sends Telegram alerts. There is no local HTTP API — the Android app reads the published JSON feed from GitHub.

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
- **Scrape listings** — every-2-hours cron + manual dispatch; commits updated `data/` when listings change

## License

Private personal project. Listing content belongs to the original publishers; use responsibly and respect their terms of service.
