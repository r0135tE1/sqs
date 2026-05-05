import asyncio
import logging
import random

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_SVG_CONCURRENCY = 20


class FlagCache:
    """Prefetches the full country dataset and all flag images from restcountries.com
    on startup so the app stays functional even if external APIs become unavailable.
    """

    def __init__(self) -> None:
        self._countries: list[dict] = []
        self._svgs: dict[str, bytes] = {}

    async def load(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{settings.restcountries_url}/all",
                    params={"fields": "name,flags,cca2"},
                )
                response.raise_for_status()
                raw = response.json()

            self._countries = [
                {
                    "name": c["name"]["common"],
                    "flag_url": c["flags"].get("svg") or c["flags"].get("png", ""),
                    "code": c.get("cca2", ""),
                }
                for c in raw
                if c.get("flags") and c.get("name", {}).get("common")
            ]
            logger.info("Flag cache loaded: %d countries", len(self._countries))
        except httpx.HTTPError as exc:
            logger.warning("Could not reach restcountries.com: %s", exc)
            return
        except (KeyError, ValueError) as exc:
            logger.warning("Unexpected response format from restcountries.com: %s", exc)
            return

        await self._load_svgs()
        # Only keep countries whose SVG was successfully cached.
        self._countries = [c for c in self._countries if c["code"] in self._svgs]
        logger.info("Countries with cached SVG: %d", len(self._countries))

    async def _load_svgs(self) -> None:
        # max 20 flags loaded at one time
        semaphore = asyncio.Semaphore(_SVG_CONCURRENCY)

        async def fetch_one(client: httpx.AsyncClient, code: str, url: str) -> tuple[str, bytes] | None:
            if not url:
                return None
            async with semaphore:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return code, resp.content
                except httpx.HTTPError as exc:
                    logger.warning("Could not fetch SVG for %s: %s", code, exc)
                    return None

        async with httpx.AsyncClient(timeout=10.0) as client:
            # wait for all SVG fetches to finish
            results = await asyncio.gather(
                *(fetch_one(client, c["code"], c["flag_url"]) for c in self._countries)
            )

        self._svgs = {code: data for code, data in (r for r in results if r is not None)}
        logger.info("SVG cache loaded: %d images", len(self._svgs))

    def get_svg(self, country_code: str) -> bytes | None:
        return self._svgs.get(country_code)

    def random_flag(self, exclude: set[str] | None = None) -> dict | None:
        if not self._countries:
            return None

        candidates = [c for c in self._countries if c["code"] not in (exclude or set())]
        if not candidates:
            return None

        entry = random.choice(candidates)

        wrong_pool = [c for c in self._countries if c["code"] != entry["code"]]
        wrong_choices = random.sample(wrong_pool, min(3, len(wrong_pool)))

        options = [entry["name"]] + [c["name"] for c in wrong_choices]
        random.shuffle(options)

        return {
            "country_code": entry["code"],
            "country_name": entry["name"],
            "options": options,
        }

    def count(self) -> int:
        return len(self._countries)


flag_cache = FlagCache()
