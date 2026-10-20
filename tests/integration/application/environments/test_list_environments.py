
import uuid

from nexus.application.environments.list_environments import ListEnvironments
from nexus.domain.environments.environment import Environment


class FakeEnvironmentRepository:
    def __init__(self, environments=None):
        self.environments = environments or []

    def list_by_project_id(self, project_id):
        return [
            environment
            for environment in self.environments
            if environment.project_id == project_id
        ]


def test_list_environments_returns_project_environments():
    project_id = uuid.uuid4()
    other_project_id = uuid.uuid4()

    environments = [
        Environment(project_id=project_id, name="production"),
        Environment(project_id=project_id, name="development"),
        Environment(project_id=other_project_id, name="staging"),
    ]

    repository = FakeEnvironmentRepository(environments)
    use_case = ListEnvironments(repository)

    result = use_case.execute(project_id)

    assert len(result) == 2
    assert {environment.name for environment in result} == {
        "production",
        "development",
    }
    assert all(environment.project_id == project_id for environment in result)


def test_list_environments_returns_empty_list():
    repository = FakeEnvironmentRepository()
    use_case = ListEnvironments(repository)

    result = use_case.execute(uuid.uuid4())

    assert result == []