from uuid import UUID

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.domain.environments.environment import Environment


class GetEnvironment:
    def __init__(self, repository: EnvironmentRepository) -> None:
        self.repository = repository

    def execute(self, environment_id: UUID) -> Environment:
        environment = self.repository.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        return environment