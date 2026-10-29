
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt


ALGORITHM = "HS256"


def _get_secret_key() -> str:
    secret = os.environ.get("JWT_SECRET_KEY", "")

    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least 32 bytes."
        )

    return secret


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)
    expires_minutes = int(
        os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    if expires_minutes <= 0:
        raise RuntimeError(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive."
        )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    return jwt.encode(
        payload,
        _get_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(
        token,
        _get_secret_key(),
        algorithms=[ALGORITHM],
        options={"require": ["sub", "iat", "exp"]},
    )

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise jwt.InvalidTokenError("Invalid subject claim.")

    try:
        return UUID(subject)
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid subject claim.") from exc
