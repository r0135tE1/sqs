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

_FAKE_SVG = b"<svg>flag</svg>"


async def test_load_success():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_COUNTRIES))
        respx.get(url__regex=r"https://flagcdn\.com/.*\.svg").mock(
            return_value=httpx.Response(200, content=_FAKE_SVG)
        )
        await cache.load()
    assert cache.count() == 3
    assert any(c["name"] == "Germany" for c in cache._countries)


async def test_load_caches_svgs():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_COUNTRIES))
        respx.get(url__regex=r"https://flagcdn\.com/.*\.svg").mock(
            return_value=httpx.Response(200, content=_FAKE_SVG)
        )
        await cache.load()
    assert cache.get_svg("DE") == _FAKE_SVG
    assert cache.get_svg("FR") == _FAKE_SVG
    assert cache.get_svg("BR") == _FAKE_SVG


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


async def test_load_svg_fetch_failure_skips_country():
    """If a single SVG fetch fails, that country is removed from the playable pool."""
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_COUNTRIES))
        respx.get("https://flagcdn.com/de.svg").mock(
            side_effect=httpx.ConnectError("timeout")
        )
        respx.get(url__regex=r"https://flagcdn\.com/(fr|br)\.svg").mock(
            return_value=httpx.Response(200, content=_FAKE_SVG)
        )
        await cache.load()
    assert cache.count() == 2
    assert cache.get_svg("DE") is None
    assert cache.get_svg("FR") == _FAKE_SVG
