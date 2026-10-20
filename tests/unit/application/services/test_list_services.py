from unittest.mock import Mock
from uuid import UUID

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.list_services import ListServices
from nexus.domain.services.service import Service


def test_services_can_be_listed():
    # Business rule:
    # Existing Services can be retrieved as a collection
    # for an Environment.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service1 = Service(
        environment_id=environment_id,
        name="API",
    )
    service2 = Service(
        environment_id=environment_id,
        name="Worker",
    )

    repository = Mock(spec=ServiceRepository)
    repository.list_by_environment_id.return_value = [
        service1,
        service2,
    ]

    use_case = ListServices(repository)

    result = use_case.execute(environment_id)

    assert result == [service1, service2]


def test_repository_lists_services_for_environment():
    # Business rule:
    # Services must be retrieved according to the Environment
    # they belong to.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.list_by_environment_id.return_value = []

    use_case = ListServices(repository)

    use_case.execute(environment_id)

    repository.list_by_environment_id.assert_called_once_with(
        environment_id
    )


def test_empty_service_list_is_valid():
    # Business rule:
    # An Environment can have zero Services.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ServiceRepository)
    repository.list_by_environment_id.return_value = []

    use_case = ListServices(repository)

    result = use_case.execute(environment_id)

    assert result == []