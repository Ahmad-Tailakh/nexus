from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.deployments.get_deployment import GetDeployment
from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.domain.deployments.deployment import Deployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError


def test_existing_deployment_can_be_retrieved():
    # Business rule:
    # An existing Deployment can be retrieved by its ID.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        id=deployment_id,
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = GetDeployment(repository)

    result = use_case.execute(deployment_id)

    assert result is deployment


def test_repository_retrieves_deployment_by_id():
    # Business rule:
    # The requested Deployment is identified by its unique ID.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        id=deployment_id,
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = GetDeployment(repository)

    use_case.execute(deployment_id)

    repository.get_by_id.assert_called_once_with(deployment_id)


def test_retrieved_deployment_is_returned():
    # Business rule:
    # GetDeployment returns the exact Deployment provided by the repository.
    service_id = UUID("87654321-4321-8765-4321-876543218765")

    deployment = Deployment(
        service_id=service_id,
    )

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = deployment

    use_case = GetDeployment(repository)

    result = use_case.execute(deployment.id)

    assert result is deployment


def test_nonexistent_deployment_raises_deployment_not_found_error():
    # Business rule:
    # The application must explicitly communicate when the requested
    # Deployment does not exist.
    deployment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=DeploymentRepository)
    repository.get_by_id.return_value = None

    use_case = GetDeployment(repository)

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id)