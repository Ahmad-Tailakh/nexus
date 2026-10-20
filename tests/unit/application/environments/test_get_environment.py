from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.environments.get_environment import GetEnvironment
from nexus.domain.environments.environment import Environment


def test_existing_environment_can_be_retrieved():
    # Business rule:
    # An existing Environment can be retrieved by its ID.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment

    use_case = GetEnvironment(repository)

    result = use_case.execute(environment_id)

    assert result is environment


def test_repository_retrieves_environment_by_id():
    # Business rule:
    # The requested Environment is identified by its unique ID.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment

    use_case = GetEnvironment(repository)

    use_case.execute(environment_id)

    repository.get_by_id.assert_called_once_with(environment_id)


def test_retrieved_environment_is_returned():
    # Business rule:
    # GetEnvironment returns the Environment provided by the repository
    # rather than creating or modifying another object.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment

    use_case = GetEnvironment(repository)

    result = use_case.execute(environment_id)

    assert result is environment


def test_nonexistent_environment_raises_environment_not_found_error():
    # Business rule:
    # The application must explicitly communicate when the requested
    # Environment does not exist.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = None

    use_case = GetEnvironment(repository)

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(environment_id)