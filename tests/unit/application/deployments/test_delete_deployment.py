from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.deployments.delete_deployment import DeleteDeployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.domain.deployments.deployment import Deployment


def test_existing_deployment_can_be_deleted():
    # Business rule:
    # An existing Deployment can be deleted.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = DeleteDeployment(repository)

    use_case.execute(deployment.id)

    repository.delete.assert_called_once_with(deployment.id)


def test_repository_retrieves_deployment_by_id():
    # Business rule:
    # The Deployment must be retrieved by its unique ID before deletion.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        id=deployment_id,
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = DeleteDeployment(repository)

    use_case.execute(deployment_id)

    repository.get_by_id.assert_called_once_with(deployment_id)


def test_existing_deployment_is_deleted():
    # Business rule:
    # When the Deployment exists, its ID is passed to the repository for deletion.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = DeleteDeployment(repository)

    use_case.execute(deployment.id)

    repository.delete.assert_called_once_with(deployment.id)


def test_nonexistent_deployment_is_rejected():
    # Business rule:
    # A Deployment that does not exist cannot be deleted.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = None

    use_case = DeleteDeployment(repository)

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id)

    repository.delete.assert_not_called()


def test_failed_deletion_does_not_delete_deployment():
    # Business rule:
    # If the Deployment cannot be found, the repository must not receive
    # a delete request.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = None

    use_case = DeleteDeployment(repository)

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id)

    repository.delete.assert_not_called()