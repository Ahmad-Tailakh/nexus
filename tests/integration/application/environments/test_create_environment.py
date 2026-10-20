import uuid

import pytest

from nexus.application.environments.create_environment import CreateEnvironment
from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.application.environments.exceptions import (
    EnvironmentNameAlreadyExistsError,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def test_create_environment_creates_environment(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    project = Project(name=f"Project-{uuid.uuid4()}")
    project_repository.save(project)

    use_case = CreateEnvironment(
        project_repository,
        environment_repository,
    )

    environment = use_case.execute(
        project_id=project.id,
        name="production",
    )

    saved_environment = environment_repository.get_by_id(environment.id)

    assert saved_environment is not None
    assert saved_environment.name == "production"
    assert saved_environment.project_id == project.id


def test_create_environment_raises_for_unknown_project(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    use_case = CreateEnvironment(
        project_repository,
        environment_repository,
    )

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(
            project_id=uuid.uuid4(),
            name="production",
        )


def test_create_environment_normalizes_name(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    project = Project(name=f"Project-{uuid.uuid4()}")
    project_repository.save(project)

    use_case = CreateEnvironment(
        project_repository,
        environment_repository,
    )

    environment = use_case.execute(
        project_id=project.id,
        name="  production  ",
    )

    assert environment.name == "production"

def test_create_environment_rejects_duplicate_name(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    project = Project(name=f"Project-{uuid.uuid4()}")
    project_repository.save(project)

    use_case = CreateEnvironment(
        project_repository,
        environment_repository,
    )

    use_case.execute(project_id=project.id, name="production")

    with pytest.raises(EnvironmentNameAlreadyExistsError):
        use_case.execute(project_id=project.id, name="production")