from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.environments.exceptions import (
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
)
from nexus.application.environments.rename_environment import RenameEnvironment
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.domain.environments.environment import Environment


def test_existing_environment_can_be_renamed():
    # Business rule:
    # An existing Environment can be renamed when the new name is available.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = False

    use_case = RenameEnvironment(repository)

    result = use_case.execute(
        environment_id=environment_id,
        new_name="Staging",
    )

    assert result is environment
    assert environment.name == "Staging"


def test_repository_retrieves_environment_by_id():
    # Business rule:
    # Rename operates on the Environment identified by its ID.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = False

    use_case = RenameEnvironment(repository)

    use_case.execute(
        environment_id=environment_id,
        new_name="Staging",
    )

    repository.get_by_id.assert_called_once_with(environment_id)


def test_repository_checks_name_with_environment_project_id():
    # Business rule:
    # Environment names are unique within their owning Project.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = False

    use_case = RenameEnvironment(repository)

    use_case.execute(
        environment_id=environment_id,
        new_name="   Staging   ",
    )

    repository.exists_by_name.assert_called_once_with(
        project_id,
        "Staging",
    )


def test_environment_name_is_normalized_through_domain():
    # Business rule:
    # Environment names are stored in normalized form.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = False

    use_case = RenameEnvironment(repository)

    use_case.execute(
        environment_id=environment_id,
        new_name="   Staging   ",
    )

    assert environment.name == "Staging"


def test_renaming_to_existing_name_is_rejected():
    # Business rule:
    # Environment names must be unique within a Project.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = True

    use_case = RenameEnvironment(repository)

    with pytest.raises(EnvironmentNameAlreadyExistsError):
        use_case.execute(
            environment_id=environment_id,
            new_name="Staging",
        )

    assert environment.name == "Production"
    repository.save.assert_not_called()


def test_nonexistent_environment_is_rejected():
    # Business rule:
    # An Environment that does not exist cannot be renamed.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = None

    use_case = RenameEnvironment(repository)

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(
            environment_id=environment_id,
            new_name="Staging",
        )

    repository.exists_by_name.assert_not_called()
    repository.save.assert_not_called()


def test_renamed_environment_is_saved():
    # Business rule:
    # A successfully renamed Environment must be persisted.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment
    repository.exists_by_name.return_value = False

    use_case = RenameEnvironment(repository)

    use_case.execute(
        environment_id=environment_id,
        new_name="Staging",
    )

    repository.save.assert_called_once_with(environment)


def test_renaming_to_whitespace_only_name_is_rejected():
    # Business rule:
    # An Environment must always have a meaningful name.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    repository = Mock(spec=EnvironmentRepository)
    repository.get_by_id.return_value = environment

    use_case = RenameEnvironment(repository)

    with pytest.raises(Exception):
        use_case.execute(
            environment_id=environment_id,
            new_name="   ",
        )

    assert environment.name == "Production"
    repository.save.assert_not_called()