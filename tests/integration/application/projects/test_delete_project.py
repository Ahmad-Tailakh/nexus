from uuid import uuid4

import pytest

from nexus.application.projects.delete_project import DeleteProject
from nexus.application.projects.exceptions import (
    ProjectHasEnvironmentsError,
    ProjectNotFoundError,
)
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.models import EnvironmentModel
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def test_delete_project_deletes_existing_project(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    use_case = DeleteProject(project_repository, environment_repository)

    project = Project(name=f"Project-{uuid4()}")
    project_repository.save(project)

    use_case.execute(project.id)

    assert project_repository.get_by_id(project.id) is None


def test_delete_project_raises_when_project_does_not_exist(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    use_case = DeleteProject(project_repository, environment_repository)

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(uuid4())


def test_delete_project_raises_when_project_has_environments(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    use_case = DeleteProject(project_repository, environment_repository)

    project = Project(name=f"Project-{uuid4()}")
    project_repository.save(project)

    environment = Environment(
        project_id=project.id,
        name="production",
    )
    session.add(
        EnvironmentModel(
            id=environment.id,
            project_id=environment.project_id,
            name=environment.name,
        )
    )
    session.commit()

    with pytest.raises(ProjectHasEnvironmentsError):
        use_case.execute(project.id)

    assert project_repository.get_by_id(project.id) is not None