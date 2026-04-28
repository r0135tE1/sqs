from app.services.flag_cache import FlagCache


def _make_countries(n: int) -> list[dict]:
    return [
        {"name": f"Country{i}", "flag_url": f"https://flagcdn.com/c{i}.svg", "code": f"C{i}"}
        for i in range(n)
    ]


def test_random_flag_empty_cache():
    cache = FlagCache()
    assert cache.random_flag() is None


def test_random_flag_returns_correct_shape():
    cache = FlagCache()
    cache._countries = _make_countries(5)
    result = cache.random_flag()
    assert result is not None
    assert {"country_code", "country_name", "flag_url", "options"} == set(result.keys())


def test_options_contain_correct_answer():
    """country_name is the correct answer kept internally — it must appear in options."""
    cache = FlagCache()
    cache._countries = _make_countries(5)
    result = cache.random_flag()
    assert result["country_name"] in result["options"]


def test_options_length_four_when_enough_countries():
    cache = FlagCache()
    cache._countries = _make_countries(10)
    result = cache.random_flag()
    assert len(result["options"]) == 4


def test_options_length_fewer_when_not_enough_countries():
    cache = FlagCache()
    cache._countries = _make_countries(3)
    result = cache.random_flag()
    # 1 correct + min(3, 2) wrong = 3 total
    assert len(result["options"]) == 3


def test_exclude_filters_correctly():
    cache = FlagCache()
    cache._countries = _make_countries(10)
    exclude = {f"C{i}" for i in range(9)}  # exclude all except C9
    result = cache.random_flag(exclude=exclude)
    assert result is not None
    assert result["country_code"] == "C9"


def test_all_excluded_returns_none():
    cache = FlagCache()
    cache._countries = _make_countries(5)
    exclude = {f"C{i}" for i in range(5)}
    assert cache.random_flag(exclude=exclude) is None


def test_count_reflects_loaded_data():
    cache = FlagCache()
    cache._countries = _make_countries(7)
    assert cache.count() == 7


def test_count_empty():
    cache = FlagCache()
    assert cache.count() == 0
