from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.application.projects.get_project import GetProject
from nexus.domain.projects.project import Project




def test_repository_retrieves_project_by_id():
    # Business rule:
    # The requested Project is identified by its unique ID.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Nexus",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project

    use_case = GetProject(repository)

    use_case.execute(project_id)

    repository.get_by_id.assert_called_once_with(project_id)


def test_retrieved_project_is_returned():
    # Business rule:
    # GetProject returns the Project provided by the repository
    # rather than creating or modifying another object.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Nexus",
        description="Nexus project",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project

    use_case = GetProject(repository)

    result = use_case.execute(project_id)

    assert result is project


def test_nonexistent_project_raises_project_not_found_error():
    # Business rule:
    # The application must explicitly communicate when the requested
    # Project does not exist.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = None

    use_case = GetProject(repository)

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(project_id)