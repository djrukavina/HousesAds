from __future__ import annotations

import argparse
import logging

from realestate_monitor.config import load_settings
from realestate_monitor.hides import apply_remote_hides
from realestate_monitor.runner import Monitor, run_forever
from realestate_monitor.store import Store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="HousesAds real-estate monitor")
    parser.add_argument("--once", action="store_true", help="Run a single scrape cycle and exit")
    args = parser.parse_args()

    settings = load_settings()
    store = Store()

    if args.once:
        monitor = Monitor(settings, store)
        try:
            hidden = apply_remote_hides(store)
            found = monitor.run_cycle()
            exported = store.export_json()
            print(f"Done. New matches this cycle: {found}")
            print(f"Newly hidden: {hidden}")
            print(f"Wrote {exported}")
        finally:
            monitor.close()
        return

    run_forever(settings, store)


if __name__ == "__main__":
    main()
