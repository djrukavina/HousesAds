from __future__ import annotations

import argparse
import logging
import threading

import uvicorn

from realestate_monitor.config import load_settings
from realestate_monitor.api import create_app
from realestate_monitor.runner import Monitor, run_forever
from realestate_monitor.store import Store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Njuškalo/Index real-estate monitor")
    parser.add_argument("--once", action="store_true", help="Run a single scrape cycle and exit")
    parser.add_argument("--api-only", action="store_true", help="Serve already scraped ads")
    args = parser.parse_args()

    settings = load_settings()
    store = Store()

    if args.once:
        monitor = Monitor(settings, store)
        try:
            found = monitor.run_cycle()
            print(f"Done. New matches this cycle: {found}")
        finally:
            monitor.close()
        return

    app = create_app(store)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="info",
        )
    )
    api_thread = threading.Thread(target=server.run, daemon=True)
    api_thread.start()
    print(f"Android API: http://{settings.api_host}:{settings.api_port}/ads")

    if args.api_only:
        api_thread.join()
        return

    run_forever(settings, store)


if __name__ == "__main__":
    main()
