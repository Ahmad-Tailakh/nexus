from uuid import UUID

from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.domain.projects.project import Project


class GetProject:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def execute(self, project_id: UUID) -> Project:
        project = self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        return project