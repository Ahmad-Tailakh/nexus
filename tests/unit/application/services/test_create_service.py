from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.service_repository import ServiceRepository
from nexus.domain.environments.environment import Environment
from nexus.application.services.create_service import CreateService



def test_service_can_be_created_for_existing_environment():
    # Business rule:
    # A Service can only be created when its parent Environment exists.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment_id,
        name="API",
    )

    assert service.environment_id == environment_id
    service_repository.save.assert_called_once_with(service)


def test_repository_retrieves_parent_environment():
    # Business rule:
    # The Service must be associated with an existing Environment.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    use_case.execute(
        environment_id=environment_id,
        name="API",
    )

    environment_repository.get_by_id.assert_called_once_with(
        environment_id
    )


def test_service_name_is_normalized_through_domain():
    # Business rule:
    # Service names must be normalized according to domain rules.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment_id,
        name="   API   ",
    )

    assert service.name == "API"


def test_service_is_saved_through_service_repository():
    # Business rule:
    # A successfully created Service must be persisted through
    # the ServiceRepository.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment_id,
        name="API",
    )

    service_repository.save.assert_called_once_with(service)


def test_created_service_is_returned():
    # Business rule:
    # CreateService returns the Service that was created and saved.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment_id,
        name="API",
    )

    saved_service = service_repository.save.call_args.args[0]

    assert service is saved_service


def test_nonexistent_environment_is_rejected():
    # Business rule:
    # A Service cannot exist without its parent Environment.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    environment_repository = Mock(spec=EnvironmentRepository)
    service_repository = Mock(spec=ServiceRepository)

    environment_repository.get_by_id.return_value = None

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(
            environment_id=environment_id,
            name="API",
        )

    service_repository.save.assert_not_called()


def test_service_receives_generated_identity():
    # Business rule:
    # Every Service must receive its own identity automatically.
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

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment_id,
        name="API",
    )

    assert service.id is not None