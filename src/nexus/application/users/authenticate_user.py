
from uuid import UUID

from nexus.application.ports.user_repository import UserRepository
from nexus.infrastructure.security.jwt_tokens import create_access_token
from nexus.infrastructure.security.passwords import verify_password


class InvalidCredentialsError(Exception):
    """Raised when the supplied credentials are invalid."""


class AuthenticateUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email.strip().lower())

        if user is None or not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError("Invalid email or password.")

        return create_access_token(user.id)
