from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.environments.exceptions import (
    EnvironmentHasServicesError,
    EnvironmentNotFoundError,
)

from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.service_repository import ServiceRepository
from nexus.domain.environments.environment import Environment


def test_existing_environment_can_be_deleted():
    # Business rule:
    # An existing Environment without Services can be deleted.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = environment
    service_repository.exists_by_environment_id.return_value = False

    from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    use_case.execute(environment_id)

    environment_repository.delete.assert_called_once_with(environment)


def test_repository_retrieves_environment_by_id():
    # Business rule:
    # The Environment to delete is identified by its unique ID.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = environment
    service_repository.exists_by_environment_id.return_value = False

    from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    use_case.execute(environment_id)

    environment_repository.get_by_id.assert_called_once_with(
        environment_id
    )


def test_environment_with_services_cannot_be_deleted():
    # Business rule:
    # An Environment cannot be deleted while Services still exist.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = environment
    service_repository.exists_by_environment_id.return_value = True

    from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentHasServicesError):
        use_case.execute(environment_id)

    environment_repository.delete.assert_not_called()


def test_environment_without_services_is_deleted():
    # Business rule:
    # An Environment can be deleted once it has no Services.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = environment
    service_repository.exists_by_environment_id.return_value = False

    from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    use_case.execute(environment_id)

    service_repository.exists_by_environment_id.assert_called_once_with(
        environment_id
    )
    environment_repository.delete.assert_called_once_with(environment)


def test_nonexistent_environment_is_rejected():
    # Business rule:
    # The application must explicitly communicate when the Environment
    # does not exist.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = None

    from nexus.application.environments.delete_environment import (
        DeleteEnvironment,
    )

    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(environment_id)

    service_repository.exists_by_environment_id.assert_not_called()
    environment_repository.delete.assert_not_called()


def test_failed_deletion_does_not_delete_environment():
    # Business rule:
    # A failed deletion must never remove the Environment.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    project_id = UUID("87654321-4321-8765-4321-876543218765")

    environment = Environment(
        id=environment_id,
        project_id=project_id,
        name="Production",
    )

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = environment
    service_repository.exists_by_environment_id.return_value = True



    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentHasServicesError):
        use_case.execute(environment_id)

    environment_repository.delete.assert_not_called()