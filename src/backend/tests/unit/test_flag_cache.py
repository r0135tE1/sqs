from app.services.flag_cache import FlagCache


def _make_countries(n: int) -> list[dict]:
    return [
        {"name": f"Country{i}", "flag_url": f"https://flagcdn.com/c{i}.svg", "code": f"C{i}"}
        for i in range(n)
    ]


def _seed_cache(cache: FlagCache, n: int) -> None:
    cache._countries = _make_countries(n)
    cache._svgs = {f"C{i}": f"<svg>flag{i}</svg>".encode() for i in range(n)}


def test_random_flag_empty_cache():
    cache = FlagCache()
    assert cache.random_flag() is None


def test_random_flag_returns_correct_shape():
    cache = FlagCache()
    _seed_cache(cache, 5)
    result = cache.random_flag()
    assert result is not None
    assert {"country_code", "country_name", "flag_svg", "options"} == set(result.keys())


def test_options_contain_correct_answer():
    """country_name is the correct answer kept internally — it must appear in options."""
    cache = FlagCache()
    _seed_cache(cache, 5)
    result = cache.random_flag()
    assert result["country_name"] in result["options"]


def test_options_length_four_when_enough_countries():
    cache = FlagCache()
    _seed_cache(cache, 10)
    result = cache.random_flag()
    assert len(result["options"]) == 4


def test_options_length_fewer_when_not_enough_countries():
    cache = FlagCache()
    _seed_cache(cache, 3)
    result = cache.random_flag()
    # 1 correct + min(3, 2) wrong = 3 total
    assert len(result["options"]) == 3


def test_exclude_filters_correctly():
    cache = FlagCache()
    _seed_cache(cache, 10)
    exclude = {f"C{i}" for i in range(9)}  # exclude all except C9
    result = cache.random_flag(exclude=exclude)
    assert result is not None
    assert result["country_code"] == "C9"


def test_all_excluded_returns_none():
    cache = FlagCache()
    _seed_cache(cache, 5)
    exclude = {f"C{i}" for i in range(5)}
    assert cache.random_flag(exclude=exclude) is None


def test_count_reflects_loaded_data():
    cache = FlagCache()
    cache._countries = _make_countries(7)
    assert cache.count() == 7


def test_count_empty():
    cache = FlagCache()
    assert cache.count() == 0


def test_get_svg_returns_cached_bytes():
    cache = FlagCache()
    cache._svgs = {"DE": b"<svg>de</svg>"}
    assert cache.get_svg("DE") == b"<svg>de</svg>"


def test_get_svg_unknown_returns_none():
    cache = FlagCache()
    assert cache.get_svg("XX") is None
