from nexus.application.ports.project_repository import ProjectRepository
from nexus.domain.projects.project import Project

from .exceptions import ProjectNameAlreadyExistsError


class CreateProject:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def execute(
        self,
        name: str,
        description: str | None = None,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
        )

        if self.repository.exists_by_name(project.name):
            raise ProjectNameAlreadyExistsError()

        self.repository.save(project)

        return project