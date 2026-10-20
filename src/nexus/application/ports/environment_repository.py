from typing import Protocol
from uuid import UUID

from nexus.domain.environments.environment import Environment


class EnvironmentRepository(Protocol):

    def save(self, environment: Environment) -> None:
        ...

    def get_by_id(self, environment_id: UUID) -> Environment | None:
        ...

    def list_by_project_id(self, project_id: UUID) -> list[Environment]:
        ...

    def delete(self, environment: Environment) -> None:
        ...

    def exists_by_name(
        self,
        project_id: UUID,
        name: str,
    ) -> bool:
        ...