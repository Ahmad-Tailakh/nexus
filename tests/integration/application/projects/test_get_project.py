from uuid import uuid4

import pytest

from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.application.projects.get_project import GetProject
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def test_get_project_returns_existing_project(session):
    repository = SqlAlchemyProjectRepository(session)

    project = Project(
        name="Nexus",
        description="Production-grade backend platform",
    )

    repository.save(project)

    use_case = GetProject(repository)

    result = use_case.execute(project.id)

    assert result.id == project.id
    assert result.name == "Nexus"
    assert result.description == "Production-grade backend platform"
    assert result.created_at == project.created_at
    assert result.updated_at == project.updated_at


def test_get_project_raises_error_for_unknown_project(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = GetProject(repository)

    unknown_id = uuid4()

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(unknown_id)

