from aiocache import cached
from typing import Annotated
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware

from cache_fastapi.Backends.memory_backend import MemoryBackend
from cache_fastapi.cacheMiddleware import CacheMiddleware

from .scraper import ClientSession
from .anthropic import AnthropicScraper

import os
import dotenv

dotenv.load_dotenv()

cache_ttl = int(os.getenv("FASTAPI_CACHE_TTL", 21600))

@cached(ttl=86400, key="anthropic_scraper")
async def get_scraper():
    session = ClientSession()
    scraper = AnthropicScraper(session=session)
    await scraper.init()
    return scraper

app = FastAPI()

cached_endpoints = [
    "/api/anthropic/pricing",
]

app.add_middleware(CacheMiddleware, backend=MemoryBackend(), cached_endpoints=cached_endpoints)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/anthropic/pricing")
async def get_anthropic_pricing(scraper: Annotated[AnthropicScraper, Depends(get_scraper)], response: Response):
    """
    Fetches the latest pricing information from the Anthropic API.
    """
    response.headers["Cache-Control"] = f"max-age={cache_ttl}"
    return await scraper.pricing_overall()

@app.on_event("shutdown")
async def shutdown_event():
    scraper = await get_scraper()
    await scraper.session.close()
