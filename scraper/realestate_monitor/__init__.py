from pathlib import Path
import os

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRAPER_ROOT.parent
LOCAL_DATA = SCRAPER_ROOT / "data"
LOCAL_DATA.mkdir(exist_ok=True)

DB_PATH = Path(os.getenv("HOUSESADS_DB_PATH", str(LOCAL_DATA / "monitor.sqlite3")))
JSON_PATH = Path(os.getenv("HOUSESADS_JSON_PATH", str(REPO_ROOT / "data" / "listings.json")))
HIDDEN_PATH = Path(os.getenv("HOUSESADS_HIDDEN_PATH", str(REPO_ROOT / "data" / "hidden.json")))

