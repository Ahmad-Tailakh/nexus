from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .exceptions import (
    EnvironmentNameRequiredError,
    InvalidEnvironmentProjectIdError,
)


@dataclass(kw_only=True)
class Environment:
    id: UUID = field(default_factory=uuid4)
    project_id: UUID
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.project_id, UUID):
            raise InvalidEnvironmentProjectIdError()

        self.name = self.normalize_name(self.name)

    @staticmethod
    def normalize_name(name: str) -> str:
        name = name.strip()

        if not name:
            raise EnvironmentNameRequiredError()

        return name

    def rename(self, name: str) -> None:
        self.name = self.normalize_name(name)