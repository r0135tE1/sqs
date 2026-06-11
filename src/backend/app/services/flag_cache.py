import asyncio
import logging
import secrets

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_rng = secrets.SystemRandom()

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
            headers = {}
            if settings.restcountries_api_key:
                headers["Authorization"] = f"Bearer {settings.restcountries_api_key}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    settings.restcountries_url,
                    headers=headers,
                )
                response.raise_for_status()
                raw = response.json()["data"]["objects"]

            self._countries = [
                {
                    "name": c["names"]["common"],
                    "flag_url": c["flag"].get("url_svg") or c["flag"].get("url_png", ""),
                    "code": c.get("codes", {}).get("alpha_2", ""),
                }
                for c in raw
                if c.get("flag") and c.get("names", {}).get("common")
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

        self._svgs = dict(filter(None, results))
        logger.info("SVG cache loaded: %d images", len(self._svgs))

    def get_svg(self, country_code: str) -> bytes | None:
        return self._svgs.get(country_code)

    def random_flag(self, exclude: set[str] | None = None) -> dict | None:
        if not self._countries:
            return None

        candidates = [c for c in self._countries if c["code"] not in (exclude or set())]
        if not candidates:
            return None

        entry = _rng.choice(candidates)

        wrong_pool = [c for c in self._countries if c["code"] != entry["code"]]
        wrong_choices = _rng.sample(wrong_pool, min(3, len(wrong_pool)))

        options = [entry["name"]] + [c["name"] for c in wrong_choices]
        _rng.shuffle(options)

        return {
            "country_code": entry["code"],
            "country_name": entry["name"],
            "flag_svg": self._svgs[entry["code"]],
            "options": options,
        }

    def count(self) -> int:
        return len(self._countries)


flag_cache = FlagCache()
