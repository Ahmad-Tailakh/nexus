from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.services.service import Service
from nexus.application.services.get_service import GetService

def test_existing_service_can_be_retrieved():
    # Business rule:
    # An existing Service can be retrieved by its ID.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = GetService(repository)

    result = use_case.execute(service_id)

    assert result is service


def test_repository_retrieves_service_by_id():
    # Business rule:
    # The requested Service is identified by its unique ID.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = GetService(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)

    repository.get_by_id.assert_called_once_with(service_id)


def test_retrieved_service_is_returned():
    # Business rule:
    # GetService returns the Service provided by the repository
    # without creating or modifying another object.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = GetService(repository)

    result = use_case.execute(service_id)

    assert result is service


def test_nonexistent_service_raises_service_not_found_error():
    # Business rule:
    # The application must explicitly communicate when the requested
    # Service does not exist.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = GetService(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)