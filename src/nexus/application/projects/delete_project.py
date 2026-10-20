from uuid import UUID

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.exceptions import (
    ProjectHasEnvironmentsError,
    ProjectNotFoundError,
)


class DeleteProject:
    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self.project_repository = project_repository
        self.environment_repository = environment_repository

    def execute(self, project_id: UUID) -> None:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        environments = self.environment_repository.list_by_project_id(
            project_id
        )

        if environments:
            raise ProjectHasEnvironmentsError()

        self.project_repository.delete(project_id)