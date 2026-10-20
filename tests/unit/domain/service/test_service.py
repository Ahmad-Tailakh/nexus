from uuid import UUID

import pytest

from nexus.domain.services.exceptions import (
    InvalidServiceEnvironmentIdError,
    ServiceNameRequiredError,
)
from nexus.domain.services.service import Service


def test_service_can_be_created_with_valid_name():
    # Business rule:
    # A Service can be created when it has a meaningful name
    # and a valid Environment identity.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service = Service(
        environment_id=environment_id,
        name="API",
    )

    assert service.name == "API"


def test_service_strips_surrounding_whitespace_from_name():
    # Business rule:
    # Service names should be stored in normalized form.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service = Service(
        environment_id=environment_id,
        name="   API   ",
    )

    assert service.name == "API"


def test_service_rejects_empty_name():
    # Business rule:
    # A Service must have a meaningful name.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    with pytest.raises(ServiceNameRequiredError):
        Service(
            environment_id=environment_id,
            name="",
        )


def test_service_rejects_whitespace_only_name():
    # Business rule:
    # Whitespace is not a meaningful Service name.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    with pytest.raises(ServiceNameRequiredError):
        Service(
            environment_id=environment_id,
            name="   ",
        )


def test_service_generates_uuid_automatically():
    # Business rule:
    # Every Service must receive its own identity automatically.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service = Service(
        environment_id=environment_id,
        name="API",
    )

    assert isinstance(service.id, UUID)


def test_service_preserves_environment_id():
    # Business rule:
    # A Service must remain associated with the Environment it belongs to.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service = Service(
        environment_id=environment_id,
        name="API",
    )

    assert service.environment_id == environment_id


def test_service_rejects_invalid_environment_id():
    # Business rule:
    # A Service must reference a valid Environment UUID.
    with pytest.raises(InvalidServiceEnvironmentIdError):
        Service(
            environment_id="not-a-uuid",
            name="API",
        )


def test_service_repository_url_defaults_to_none():
    # Business rule:
    # Repository information is optional for a Service.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service = Service(
        environment_id=environment_id,
        name="API",
    )

    assert service.repository_url is None


def test_service_can_store_repository_url():
    # Business rule:
    # Nexus can store repository information associated with a Service.
    # URL syntax validation is intentionally not a domain rule yet.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")
    repository_url = "https://github.com/example/nexus-api"

    service = Service(
        environment_id=environment_id,
        name="API",
        repository_url=repository_url,
    )

    assert service.repository_url == repository_url


def test_two_services_receive_different_uuids():
    # Business rule:
    # Separate Service instances must have distinct identities.
    environment_id = UUID("12345678-1234-5678-1234-567812345678")

    service1 = Service(
        environment_id=environment_id,
        name="API",
    )
    service2 = Service(
        environment_id=environment_id,
        name="Worker",
    )

    assert service1.id != service2.id

