import httpx
import respx

from app.config import settings
from app.services.flag_cache import FlagCache

_API_URL = f"{settings.restcountries_url}/all"

MOCK_COUNTRIES = [
    {"name": {"common": "Germany"}, "flags": {"svg": "https://flagcdn.com/de.svg"}, "cca2": "DE"},
    {"name": {"common": "France"}, "flags": {"svg": "https://flagcdn.com/fr.svg"}, "cca2": "FR"},
    {"name": {"common": "Brazil"}, "flags": {"svg": "https://flagcdn.com/br.svg"}, "cca2": "BR"},
]


async def test_load_success():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_COUNTRIES))
        await cache.load()
    assert cache.count() == 3
    assert any(c["name"] == "Germany" for c in cache._countries)


async def test_load_http_error():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(side_effect=httpx.ConnectError("Connection refused"))
        await cache.load()
    assert cache.count() == 0


async def test_load_bad_json():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, text="this is not json"))
        await cache.load()
    assert cache.count() == 0


async def test_load_non_200_status():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(500))
        await cache.load()
    assert cache.count() == 0
