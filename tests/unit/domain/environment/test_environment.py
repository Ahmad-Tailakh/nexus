from uuid import UUID

import pytest

from nexus.domain.environments.environment import Environment
from nexus.domain.environments.exceptions import (
    EnvironmentNameRequiredError,
    InvalidEnvironmentProjectIdError,
)


def test_environment_can_be_created_with_valid_name():
    # Business rule:
    # An Environment can be created when it has a meaningful name
    # and a valid Project identity.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment = Environment(
        project_id=project_id,
        name="Production",
    )

    assert environment.name == "Production"


def test_environment_strips_surrounding_whitespace_from_name():
    # Business rule:
    # Environment names should be stored in normalized form.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment = Environment(
        project_id=project_id,
        name="   Production   ",
    )

    assert environment.name == "Production"


def test_environment_rejects_empty_name():
    # Business rule:
    # An Environment must have a meaningful name.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    with pytest.raises(EnvironmentNameRequiredError):
        Environment(
            project_id=project_id,
            name="",
        )


def test_environment_rejects_whitespace_only_name():
    # Business rule:
    # Whitespace is not a meaningful Environment name.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    with pytest.raises(EnvironmentNameRequiredError):
        Environment(
            project_id=project_id,
            name="   ",
        )


def test_environment_generates_uuid_automatically():
    # Business rule:
    # Every Environment must receive its own identity automatically.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment = Environment(
        project_id=project_id,
        name="Production",
    )

    assert isinstance(environment.id, UUID)


def test_environment_preserves_project_id():
    # Business rule:
    # An Environment must remain associated with the Project it belongs to.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment = Environment(
        project_id=project_id,
        name="Production",
    )

    assert environment.project_id == project_id


def test_environment_rejects_invalid_project_id():
    # Business rule:
    # An Environment must reference a valid Project UUID.
    with pytest.raises(InvalidEnvironmentProjectIdError):
        Environment(
            project_id="not-a-uuid",
            name="Production",
        )


def test_two_environments_receive_different_uuids():
    # Business rule:
    # Separate Environment instances must have distinct identities.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    environment1 = Environment(
        project_id=project_id,
        name="Production",
    )
    environment2 = Environment(
        project_id=project_id,
        name="Development",
    )

    assert environment1.id != environment2.id