from app.services.auth import create_token, decode_token, hash_password, verify_password


def test_hash_password_is_not_plaintext():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"


def test_verify_password_correct():
    hashed = hash_password("mysecret")
    assert verify_password("mysecret", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mysecret")
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    token = create_token("alice")
    assert decode_token(token) == "alice"


def test_decode_invalid_token_returns_none():
    assert decode_token("not.a.valid.token") is None
