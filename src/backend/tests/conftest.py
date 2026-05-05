import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-do-not-use-in-prod")

import pytest

from app.services.flag_cache import flag_cache

FAKE_COUNTRIES = [
    {"name": f"Country{i}", "flag_url": f"https://flagcdn.com/c{i}.svg", "code": f"C{i}"}
    for i in range(10)
]

FAKE_SVGS = {f"C{i}": f"<svg>flag{i}</svg>".encode() for i in range(10)}


@pytest.fixture
def seeded_flag_cache():
    original_countries = list(flag_cache._countries)
    original_svgs = dict(flag_cache._svgs)
    flag_cache._countries = list(FAKE_COUNTRIES)
    flag_cache._svgs = dict(FAKE_SVGS)
    yield flag_cache
    flag_cache._countries = original_countries
    flag_cache._svgs = original_svgs
