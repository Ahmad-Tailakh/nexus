from uuid import UUID

from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.create_project import (
    ProjectNameAlreadyExistsError,
)
from nexus.domain.projects.project import Project

from .exceptions import ProjectNotFoundError


class RenameProject:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def execute(self, project_id: UUID, new_name: str) -> Project:
        project = self.repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        normalized_name = Project.normalize_name(new_name)

        if self.repository.exists_by_name(normalized_name):
            raise ProjectNameAlreadyExistsError()

        project.rename(normalized_name)

        self.repository.save(project)

        return project