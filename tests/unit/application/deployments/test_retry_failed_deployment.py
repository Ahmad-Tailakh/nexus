from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.deployments.retry_failed_deployment import (
    RetryFailedDeployment,
)
from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.domain.deployments.deployment import Deployment
from nexus.domain.deployments.status import DeploymentStatus


def test_failed_deployment_can_be_retried():
    # Business rule:
    # A failed Deployment can be retried and returns to PENDING.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )
    deployment.start()
    deployment.fail()

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = RetryFailedDeployment(repository)

    result = use_case.execute(deployment.id)

    assert result.status == DeploymentStatus.PENDING


def test_repository_retrieves_deployment_by_id():
    # Business rule:
    # The Deployment to retry is identified by its unique ID.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )
    deployment.start()
    deployment.fail()

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = RetryFailedDeployment(repository)

    use_case.execute(deployment.id)

    repository.get_by_id.assert_called_once_with(deployment.id)


def test_retried_deployment_is_saved():
    # Business rule:
    # A successfully retried Deployment must be persisted.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )
    deployment.start()
    deployment.fail()

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = RetryFailedDeployment(repository)

    use_case.execute(deployment.id)

    repository.save.assert_called_once_with(deployment)


def test_retried_deployment_is_returned():
    # Business rule:
    # RetryFailedDeployment returns the same Deployment instance
    # that was retrieved and modified.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )
    deployment.start()
    deployment.fail()

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = RetryFailedDeployment(repository)

    result = use_case.execute(deployment.id)

    assert result is deployment


def test_nonexistent_deployment_is_rejected():
    # Business rule:
    # A Deployment that does not exist cannot be retried.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = None

    use_case = RetryFailedDeployment(repository)

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id)

    repository.save.assert_not_called()


def test_non_failed_deployment_cannot_be_retried():
    # Business rule:
    # Only a FAILED Deployment can be retried.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = RetryFailedDeployment(repository)

    with pytest.raises(Exception):
        use_case.execute(deployment.id)

    repository.save.assert_not_called()