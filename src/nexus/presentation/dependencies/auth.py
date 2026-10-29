
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from nexus.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from nexus.infrastructure.security.jwt_tokens import decode_access_token
from nexus.presentation.dependencies.db import get_db_session


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db_session),
):
    print("AUTH: get_current_user called")
    print("AUTH: credentials present:", credentials is not None)

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        print("AUTH FAIL: no credentials")
        raise unauthorized

    try:
        user_id = decode_access_token(credentials.credentials)
        print("AUTH: token decoded, user_id:", user_id)
    except (jwt.InvalidTokenError, RuntimeError) as exc:
        print("AUTH FAIL: token decoding:", type(exc).__name__, str(exc))
        raise unauthorized from None

    user = SqlAlchemyUserRepository(session).get_by_id(user_id)
    print("AUTH: user found:", user is not None)

    if user is None:
        raise unauthorized

    return user
