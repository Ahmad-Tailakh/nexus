from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .exceptions import (
    InvalidServiceEnvironmentIdError,
    ServiceNameRequiredError,
)


@dataclass(kw_only=True)
class Service:
    id: UUID = field(default_factory=uuid4)
    environment_id: UUID
    name: str
    repository_url: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.environment_id, UUID):
            raise InvalidServiceEnvironmentIdError()

        self.name = self.normalize_name(self.name)

    @staticmethod
    def normalize_name(name: str) -> str:
        name = name.strip()

        if not name:
            raise ServiceNameRequiredError()

        return name

    def update_repository_url(self, repository_url: str | None) -> None:
        self.repository_url = repository_url