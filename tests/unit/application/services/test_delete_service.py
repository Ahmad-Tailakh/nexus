from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.delete_service import DeleteService
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.services.service import Service


def test_existing_service_can_be_deleted():
    # Business rule:
    # An existing Service can be deleted.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = DeleteService(repository)
    use_case.execute(service_id)

    repository.get_by_id.assert_called_once_with(service_id)
    repository.delete.assert_called_once_with(service_id)


def test_repository_retrieves_service_by_id():
    # Business rule:
    # The Service to delete is identified by its unique ID.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = DeleteService(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)

    repository.get_by_id.assert_called_once_with(service_id)
    repository.delete.assert_not_called()


def test_existing_service_is_deleted():
    # Business rule:
    # The repository receives the Service ID for deletion.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = DeleteService(repository)
    use_case.execute(service_id)

    repository.delete.assert_called_once_with(service_id)


def test_nonexistent_service_is_rejected():
    # Business rule:
    # A Service that does not exist cannot be deleted.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = DeleteService(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)

    repository.delete.assert_not_called()


def test_failed_deletion_does_not_delete_service():
    # Business rule:
    # If the Service cannot be found, the repository must not delete anything.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = DeleteService(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id)

    repository.delete.assert_not_called()