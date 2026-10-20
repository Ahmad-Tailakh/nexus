from uuid import UUID

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.application.environments.exceptions import (
    EnvironmentNameAlreadyExistsError,
)
from nexus.domain.environments.environment import Environment


class CreateEnvironment:
    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self.project_repository = project_repository
        self.environment_repository = environment_repository

    def execute(
        self,
        project_id: UUID,
        name: str,
    ) -> Environment:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        normalized_name = Environment.normalize_name(name)

        if self.environment_repository.exists_by_name(
            project_id,
            normalized_name,
        ):
            raise EnvironmentNameAlreadyExistsError()

        environment = Environment(
            project_id=project.id,
            name=normalized_name,
        )

        self.environment_repository.save(environment)

        return environment