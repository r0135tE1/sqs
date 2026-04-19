from app.services.flag_cache import FlagCache


def test_count_empty():
    cache = FlagCache()
    assert cache.count() == 0


def test_random_flag_empty_returns_none():
    cache = FlagCache()
    assert cache.random_flag() is None


def test_random_flag_returns_flag():
    cache = FlagCache()
    cache._countries = [
        {"name": "Germany", "flag_url": "https://flagcdn.com/de.svg", "code": "DE"},
        {"name": "France",  "flag_url": "https://flagcdn.com/fr.svg", "code": "FR"},
        {"name": "Spain",   "flag_url": "https://flagcdn.com/es.svg", "code": "ES"},
        {"name": "Italy",   "flag_url": "https://flagcdn.com/it.svg", "code": "IT"},
    ]
    flag = cache.random_flag()
    assert flag is not None
    assert "country_code" in flag
    assert "country_name" in flag
    assert "flag_url" in flag
    assert "options" in flag
    assert len(flag["options"]) == 4
    assert flag["country_name"] in flag["options"]


def test_random_flag_excludes_seen():
    cache = FlagCache()
    cache._countries = [
        {"name": "Germany", "flag_url": "https://flagcdn.com/de.svg", "code": "DE"},
        {"name": "France",  "flag_url": "https://flagcdn.com/fr.svg", "code": "FR"},
    ]
    flag = cache.random_flag(exclude={"DE"})
    assert flag["country_code"] == "FR"


def test_random_flag_all_excluded_returns_none():
    cache = FlagCache()
    cache._countries = [
        {"name": "Germany", "flag_url": "https://flagcdn.com/de.svg", "code": "DE"},
    ]
    assert cache.random_flag(exclude={"DE"}) is None


def test_count_returns_correct_number():
    cache = FlagCache()
    cache._countries = [{"name": "X", "flag_url": "", "code": "XX"}] * 5
    assert cache.count() == 5
