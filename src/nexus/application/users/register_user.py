
from nexus.application.ports.user_repository import UserRepository
from nexus.application.users.errors import EmailAlreadyRegisteredError
from nexus.application.users.password_policy import validate_password
from nexus.domain.users.user import User
from nexus.infrastructure.security.passwords import hash_password


class RegisterUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, email: str, password: str) -> User:
        validate_password(password)

        normalized_email = email.strip().lower()

        if self.user_repository.get_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists."
            )

        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
        )

        self.user_repository.save(user)

        return user
