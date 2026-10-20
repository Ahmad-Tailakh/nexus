from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.application.services.update_repository_url import (
    UpdateRepositoryUrl,
)
from nexus.domain.services.service import Service


def test_existing_service_repository_url_can_be_updated():
    # Business rule:
    # An existing Service's repository URL can be changed.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
        repository_url="https://github.com/old/repository",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = UpdateRepositoryUrl(repository)

    result = use_case.execute(
        service_id,
        "https://github.com/new/repository",
    )

    assert result.repository_url == "https://github.com/new/repository"


def test_repository_retrieves_service_by_id():
    # Business rule:
    # The Service being updated is identified by its unique ID.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = UpdateRepositoryUrl(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id, "https://github.com/example/repository")

    repository.get_by_id.assert_called_once_with(service_id)


def test_updated_service_is_saved():
    # Business rule:
    # A successfully updated Service must be persisted.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
        repository_url="https://github.com/old/repository",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = UpdateRepositoryUrl(repository)

    use_case.execute(
        service_id,
        "https://github.com/new/repository",
    )

    repository.save.assert_called_once_with(service)


def test_updated_service_is_returned():
    # Business rule:
    # The updated Service is returned to the caller.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = UpdateRepositoryUrl(repository)

    result = use_case.execute(
        service_id,
        "https://github.com/example/repository",
    )

    assert result is service


def test_repository_url_can_be_cleared():
    # Business rule:
    # A Service may have no repository URL.
    service_id = UUID("12345678-1234-5678-1234-567812345678")
    environment_id = UUID("87654321-4321-8765-4321-876543218765")

    service = Service(
        id=service_id,
        environment_id=environment_id,
        name="API",
        repository_url="https://github.com/example/repository",
    )

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = service

    use_case = UpdateRepositoryUrl(repository)

    result = use_case.execute(service_id, None)

    assert result.repository_url is None


def test_nonexistent_service_is_rejected():
    # Business rule:
    # A repository URL cannot be updated for a Service that does not exist.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.get_by_id.return_value = None

    use_case = UpdateRepositoryUrl(repository)

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id, None)

    repository.save.assert_not_called()