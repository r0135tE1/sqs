import httpx
import respx

from app.config import settings
from app.services.flag_cache import FlagCache

_API_URL = settings.restcountries_url

MOCK_COUNTRIES = [
    {"names": {"common": "Germany"}, "flag": {"url_svg": "https://flagcdn.com/de.svg", "url_png": ""}, "codes": {"alpha_2": "DE"}},
    {"names": {"common": "France"}, "flag": {"url_svg": "https://flagcdn.com/fr.svg", "url_png": ""}, "codes": {"alpha_2": "FR"}},
    {"names": {"common": "Brazil"}, "flag": {"url_svg": "https://flagcdn.com/br.svg", "url_png": ""}, "codes": {"alpha_2": "BR"}},
]

MOCK_RESPONSE = {"data": {"objects": MOCK_COUNTRIES}}

_FAKE_SVG = b"<svg>flag</svg>"


async def test_load_success():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_RESPONSE))
        respx.get(url__regex=r"https://flagcdn\.com/.*\.svg").mock(
            return_value=httpx.Response(200, content=_FAKE_SVG)
        )
        await cache.load()
    assert cache.count() == 3
    assert any(c["name"] == "Germany" for c in cache._countries)


async def test_load_caches_svgs():
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_RESPONSE))
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
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_RESPONSE))
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


# ---------------------------------------------------------------------------
# DB persistence and fallback
# ---------------------------------------------------------------------------

async def test_load_success_persists_to_db(db_session):
    """On a successful API load, all flags are written to the database."""
    from app.repositories.flag import FlagRepository
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(return_value=httpx.Response(200, json=MOCK_RESPONSE))
        respx.get(url__regex=r"https://flagcdn\.com/.*\.svg").mock(
            return_value=httpx.Response(200, content=_FAKE_SVG)
        )
        await cache.load(db=db_session)

    rows = await FlagRepository(db_session).get_all()
    assert len(rows) == 3
    assert {r.code for r in rows} == {"DE", "FR", "BR"}


async def test_load_http_error_falls_back_to_db(db_session):
    """When the API is unreachable and the DB has data, flags are loaded from the DB."""
    from app.repositories.flag import FlagRepository
    await FlagRepository(db_session).upsert_all([
        {"code": "DE", "name": "Germany", "flag_svg": _FAKE_SVG},
        {"code": "FR", "name": "France", "flag_svg": _FAKE_SVG},
    ])

    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(side_effect=httpx.ConnectError("timeout"))
        await cache.load(db=db_session)

    assert cache.count() == 2
    assert cache.get_svg("DE") == _FAKE_SVG
    assert cache.get_svg("FR") == _FAKE_SVG


async def test_load_http_error_empty_db_stays_empty(db_session):
    """When the API is unreachable and the DB is empty, the cache stays empty."""
    cache = FlagCache()
    with respx.mock:
        respx.get(_API_URL).mock(side_effect=httpx.ConnectError("timeout"))
        await cache.load(db=db_session)

    assert cache.count() == 0