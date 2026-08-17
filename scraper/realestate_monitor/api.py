from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .store import Store


def create_app(store: Store) -> FastAPI:
    app = FastAPI(title="NjuskaloAds scraper")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ads")
    def ads() -> dict[str, list[dict]]:
        return {"ads": [item.to_api() for item in store.all_listings()]}

    return app
