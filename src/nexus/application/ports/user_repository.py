
from abc import ABC, abstractmethod
from uuid import UUID

from nexus.domain.users.user import User


class UserRepository(ABC):
    """Port for user persistence."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass
