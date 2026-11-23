from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_the_plain_password():
    hashed = hash_password("correct-horse")
    assert hashed != "correct-horse"
    assert hashed.startswith("$2")


def test_verify_password_accepts_match_and_rejects_mismatch():
    hashed = hash_password("correct-horse")
    assert verify_password("correct-horse", hashed) is True
    assert verify_password("wrong-horse", hashed) is False


def test_verify_password_rejects_garbage_hash():
    assert verify_password("correct-horse", "not-a-bcrypt-hash") is False


def test_access_token_round_trip():
    token = create_access_token(7)
    assert decode_access_token(token) == 7


def test_decode_rejects_tampered_token():
    token = create_access_token(7)
    with pytest.raises(ValueError):
        decode_access_token(token + "x")


def test_decode_rejects_expired_token():
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "7", "exp": expired},
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(ValueError):
        decode_access_token(token)
