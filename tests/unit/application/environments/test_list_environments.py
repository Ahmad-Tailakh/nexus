from unittest.mock import Mock
from uuid import UUID

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.environments.list_environments import ListEnvironments
from nexus.domain.environments.environment import Environment


def test_environments_can_be_listed_for_a_project():
    # Business rule:
    # A Project's Environments can be retrieved as a collection.

    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment1 = Environment(
        project_id=project_id,
        name="Production",
    )
    environment2 = Environment(
        project_id=project_id,
        name="Development",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.list_by_project_id.return_value = [
        environment1,
        environment2,
    ]

    use_case = ListEnvironments(repository)

    result = use_case.execute(project_id)

    assert result == [environment1, environment2]

def test_repository_lists_environments_for_project():
    # Business rule:
    # Environment retrieval must be scoped to the owning Project.

    project_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=EnvironmentRepository)
    repository.list_by_project_id.return_value = []

    use_case = ListEnvironments(repository)

    use_case.execute(project_id)

    repository.list_by_project_id.assert_called_once_with(project_id)

def test_empty_environment_list_is_valid():
    # Business rule:
    # A Project may exist without any Environments.

    project_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=EnvironmentRepository)
    repository.list_by_project_id.return_value = []

    use_case = ListEnvironments(repository)

    result = use_case.execute(project_id)

    assert result == []