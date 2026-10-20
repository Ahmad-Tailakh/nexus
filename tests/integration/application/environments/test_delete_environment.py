
import uuid

import pytest

from nexus.application.environments.delete_environment import DeleteEnvironment
from nexus.application.environments.exceptions import (
    EnvironmentHasServicesError,
    EnvironmentNotFoundError,
)
from nexus.domain.environments.environment import Environment


class FakeEnvironmentRepository:
    def __init__(self, environment=None):
        self.environment = environment
        self.deleted = False

    def get_by_id(self, environment_id):
        if self.environment and self.environment.id == environment_id:
            return self.environment
        return None

    def delete(self, environment):
        self.deleted = True
        self.environment = None


class FakeServiceRepository:
    def __init__(self, has_services=False):
        self.has_services = has_services

    def exists_by_environment_id(self, environment_id):
        return self.has_services


def test_delete_environment_deletes_environment():
    environment = Environment(
        project_id=uuid.uuid4(),
        name="production",
    )
    environment_repository = FakeEnvironmentRepository(environment)
    service_repository = FakeServiceRepository()
    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    use_case.execute(environment.id)

    assert environment_repository.deleted is True
    assert environment_repository.environment is None


def test_delete_environment_raises_for_unknown_environment():
    environment_repository = FakeEnvironmentRepository()
    service_repository = FakeServiceRepository()
    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(uuid.uuid4())

    assert environment_repository.deleted is False


def test_delete_environment_rejects_environment_with_services():
    environment = Environment(
        project_id=uuid.uuid4(),
        name="production",
    )
    environment_repository = FakeEnvironmentRepository(environment)
    service_repository = FakeServiceRepository(has_services=True)
    use_case = DeleteEnvironment(
        environment_repository,
        service_repository,
    )

    with pytest.raises(EnvironmentHasServicesError):
        use_case.execute(environment.id)

    assert environment_repository.deleted is False