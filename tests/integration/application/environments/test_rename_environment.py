
import uuid

import pytest

from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.environments.rename_environment import RenameEnvironment
from nexus.domain.environments.environment import Environment


class FakeEnvironmentRepository:
    def __init__(self, environment=None):
        self.environment = environment

    def get_by_id(self, environment_id):
        if self.environment and self.environment.id == environment_id:
            return self.environment
        return None

    def save(self, environment):
        self.environment = environment

    def exists_by_name(self, project_id, name):
        return (
            self.environment is not None
            and self.environment.project_id == project_id
            and self.environment.name == name
        )


def test_rename_environment_updates_name():
    environment = Environment(
        project_id=uuid.uuid4(),
        name="development",
    )
    repository = FakeEnvironmentRepository(environment)
    use_case = RenameEnvironment(repository)

    result = use_case.execute(
        environment_id=environment.id,
        new_name="production",
    )

    assert result.name == "production"


def test_rename_environment_raises_for_unknown_environment():
    repository = FakeEnvironmentRepository()
    use_case = RenameEnvironment(repository)

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(
            environment_id=uuid.uuid4(),
            new_name="production",
        )