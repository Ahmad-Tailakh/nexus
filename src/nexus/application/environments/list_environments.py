from uuid import UUID

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.domain.environments.environment import Environment


class ListEnvironments:
    def __init__(self, repository: EnvironmentRepository) -> None:
        self.repository = repository

    def execute(self, project_id: UUID) -> list[Environment]:
        return self.repository.list_by_project_id(project_id)