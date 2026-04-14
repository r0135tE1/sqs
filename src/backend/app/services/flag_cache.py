import logging
import random

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FlagCache:
    """Prefetches the full country dataset from restcountries.com on startup.

    Serves random flags from the in-memory cache so the app stays functional
    even if the external API is temporarily unavailable (ADR-006).
    """

    def __init__(self) -> None:
        self._countries: list[dict] = []

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
        except (KeyError, ValueError) as exc:
            logger.warning("Unexpected response format from restcountries.com: %s", exc)

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
            "flag_url": entry["flag_url"],
            "options": options,
        }

    def count(self) -> int:
        return len(self._countries)


flag_cache = FlagCache()
