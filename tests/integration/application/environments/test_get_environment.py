
import uuid

import pytest

from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.environments.get_environment import GetEnvironment
from nexus.domain.environments.environment import Environment


class FakeEnvironmentRepository:
    def __init__(self, environment=None):
        self.environment = environment

    def get_by_id(self, environment_id):
        if self.environment and self.environment.id == environment_id:
            return self.environment
        return None


def test_get_environment_returns_environment():
    environment = Environment(
        project_id=uuid.uuid4(),
        name="production",
    )
    repository = FakeEnvironmentRepository(environment)
    use_case = GetEnvironment(repository)

    result = use_case.execute(environment.id)

    assert result.id == environment.id
    assert result.name == "production"
    assert result.project_id == environment.project_id


def test_get_environment_raises_for_unknown_environment():
    repository = FakeEnvironmentRepository()
    use_case = GetEnvironment(repository)

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(uuid.uuid4())