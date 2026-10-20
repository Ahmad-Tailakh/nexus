from uuid import uuid4

from nexus.domain.projects.project import Project
from nexus.infrastructure.database.models import EnvironmentModel
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def test_list_by_project_id_returns_only_project_environments(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    project = Project(name=f"Project-{uuid4()}")
    other_project = Project(name=f"Project-{uuid4()}")

    project_repository.save(project)
    project_repository.save(other_project)

    session.add_all(
        [
            EnvironmentModel(
                id=uuid4(),
                project_id=project.id,
                name="production",
            ),
            EnvironmentModel(
                id=uuid4(),
                project_id=project.id,
                name="development",
            ),
            EnvironmentModel(
                id=uuid4(),
                project_id=other_project.id,
                name="staging",
            ),
        ]
    )
    session.commit()

    environments = environment_repository.list_by_project_id(project.id)

    assert len(environments) == 2
    assert {environment.name for environment in environments} == {
        "production",
        "development",
    }
    assert all(
        environment.project_id == project.id
        for environment in environments
    )