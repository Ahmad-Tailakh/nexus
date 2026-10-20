from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.application.deployments.create_deployment import CreateDeployment
from nexus.domain.deployments.deployment import Deployment
from nexus.domain.services.service import Service


def test_deployment_can_be_created_for_existing_service():
    # Business rule:
    # A Deployment can only be created for an existing Service.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    result = use_case.execute(service_id)

    assert isinstance(result, Deployment)


def test_repository_retrieves_parent_service_by_id():
    # Business rule:
    # The requested Service is identified by its unique ID.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    use_case.execute(service_id)

    service_repository.get_by_id.assert_called_once_with(service_id)


def test_deployment_is_saved_through_deployment_repository():
    # Business rule:
    # A successfully created Deployment must be persisted.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    result = use_case.execute(service_id)

    deployment_repository.save.assert_called_once_with(result)


def test_created_deployment_is_returned():
    # Business rule:
    # CreateDeployment returns the newly created Deployment.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    result = use_case.execute(service_id)

    assert isinstance(result, Deployment)


def test_deployment_preserves_service_id():
    # Business rule:
    # The created Deployment must remain associated with the requested Service.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    result = use_case.execute(service_id)

    assert result.service_id == service_id


def test_nonexistent_service_is_rejected():
    # Business rule:
    # A Deployment cannot be created when its parent Service does not exist.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service_repository.get_by_id.return_value = None

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)

    deployment_repository.save.assert_not_called()


def test_deployment_receives_generated_identity():
    # Business rule:
    # Every newly created Deployment must receive its own generated identity.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    service_repository = Mock(spec=ServiceRepository)
    deployment_repository = Mock(spec=DeploymentRepository)

    service = Service(
        environment_id=UUID("87654321-4321-8765-4321-876543218765"),
        name="API",
    )
    service.id = service_id

    service_repository.get_by_id.return_value = service

    use_case = CreateDeployment(
        service_repository,
        deployment_repository,
    )

    result = use_case.execute(service_id)

    assert isinstance(result.id, UUID)