import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-do-not-use-in-prod")

import pytest

from app.services.flag_cache import flag_cache

FAKE_COUNTRIES = [
    {"name": f"Country{i}", "flag_url": f"https://flagcdn.com/c{i}.svg", "code": f"C{i}"}
    for i in range(10)
]


@pytest.fixture
def seeded_flag_cache():
    original = list(flag_cache._countries)
    flag_cache._countries = list(FAKE_COUNTRIES)
    yield flag_cache
    flag_cache._countries = original
