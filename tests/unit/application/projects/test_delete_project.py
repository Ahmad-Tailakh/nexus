import pytest
from uuid import uuid4

from nexus.application.projects.delete_project import (
    DeleteProject,
    ProjectHasEnvironmentsError,
)
from nexus.application.projects.get_project import ProjectNotFoundError
from nexus.domain.projects.project import Project


class FakeProjectRepository:
    def __init__(self) -> None:
        self.projects: dict = {}
        self.deleted_ids: list = []

    def exists_by_name(self, name: str) -> bool:
        return any(project.name == name for project in self.projects.values())

    def get_by_id(self, project_id):
        return self.projects.get(project_id)

    def save(self, project: Project) -> None:
        self.projects[project.id] = project

    def list_all(self) -> list[Project]:
        return list(self.projects.values())

    def delete(self, project_id) -> None:
        self.deleted_ids.append(project_id)
        self.projects.pop(project_id, None)


class FakeEnvironmentRepository:
    def __init__(self) -> None:
        self.environments_by_project: dict = {}

    def save(self, environment) -> None:
        self.environments_by_project.setdefault(
            environment.project_id, []
        ).append(environment)

    def get_by_id(self, environment_id):
        for environments in self.environments_by_project.values():
            for environment in environments:
                if environment.id == environment_id:
                    return environment
        return None

    def list_by_project_id(self, project_id):
        return self.environments_by_project.get(project_id, [])

    def delete(self, environment) -> None:
        environments = self.environments_by_project.get(
            environment.project_id, []
        )
        if environment in environments:
            environments.remove(environment)

    def exists_by_name(self, project_id, name) -> bool:
        return any(
            environment.name == name
            for environment in self.list_by_project_id(project_id)
        )


@pytest.fixture
def repositories():
    return FakeProjectRepository(), FakeEnvironmentRepository()


def test_delete_project_without_environments(repositories):
    project_repository, environment_repository = repositories
    project = Project(id=uuid4(), name="my-project", description=None)
    project_repository.save(project)

    use_case = DeleteProject(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    use_case.execute(project.id)

    assert project_repository.get_by_id(project.id) is None
    assert project.id in project_repository.deleted_ids


def test_delete_project_with_environments_is_rejected(repositories):
    project_repository, environment_repository = repositories
    project = Project(id=uuid4(), name="my-project", description=None)
    project_repository.save(project)

    # We only need a non-empty result to test the deletion rule.
    environment_repository.environments_by_project[project.id] = [object()]

    use_case = DeleteProject(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    with pytest.raises(ProjectHasEnvironmentsError):
        use_case.execute(project.id)

    assert project_repository.get_by_id(project.id) is project
    assert project.id not in project_repository.deleted_ids


def test_delete_nonexistent_project_raises_error(repositories):
    project_repository, environment_repository = repositories
    project_id = uuid4()

    use_case = DeleteProject(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(project_id)

    assert project_id not in project_repository.deleted_ids