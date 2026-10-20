from typing import Protocol
from uuid import UUID

from nexus.domain.projects.project import Project


class ProjectRepository(Protocol):

    def exists_by_name(self, name: str) -> bool:
        ...

    def get_by_id(self, project_id: UUID) -> Project | None:
        ...

    def save(self, project: Project) -> None:
        ...

    def list_all(self) -> list[Project]:
        ...

    def delete(self, project_id: UUID) -> None:
        ...