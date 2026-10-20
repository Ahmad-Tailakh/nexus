from uuid import UUID

from nexus.application.environments.exceptions import (
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
)
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.domain.environments.environment import Environment


class RenameEnvironment:
    def __init__(self, repository: EnvironmentRepository) -> None:
        self.repository = repository

    def execute(
        self,
        environment_id: UUID,
        new_name: str,
    ) -> Environment:
        environment = self.repository.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        normalized_name = Environment.normalize_name(new_name)

        if self.repository.exists_by_name(
            environment.project_id,
            normalized_name,
        ):
            raise EnvironmentNameAlreadyExistsError()

        environment.rename(normalized_name)

        self.repository.save(environment)

        return environment