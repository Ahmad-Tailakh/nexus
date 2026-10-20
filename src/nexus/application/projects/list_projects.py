from nexus.application.ports.project_repository import ProjectRepository
from nexus.domain.projects.project import Project


class ListProjects:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def execute(self) -> list[Project]:
        return self.repository.list_all()