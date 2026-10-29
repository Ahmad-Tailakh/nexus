
from uuid import uuid4

import jwt
import pytest

from nexus.infrastructure.security.jwt_tokens import (
    create_access_token,
    decode_access_token,
)


@pytest.fixture
def jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")


def test_access_token_round_trip(jwt_secret):
    user_id = uuid4()

    token = create_access_token(user_id)

    assert decode_access_token(token) == user_id


def test_invalid_signature_is_rejected(jwt_secret):
    token = create_access_token(uuid4())

    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(
            token,
            "wrong-secret" * 5,
            algorithms=["HS256"],
        )


def test_expired_token_is_rejected(jwt_secret):
    from datetime import UTC, datetime, timedelta

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": datetime.now(UTC) - timedelta(minutes=10),
            "exp": datetime.now(UTC) - timedelta(minutes=5),
        },
        "x" * 48,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_missing_secret_is_rejected(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError):
        create_access_token(uuid4())
