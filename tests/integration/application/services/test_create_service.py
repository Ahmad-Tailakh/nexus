import uuid

import pytest

from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.services.create_service import CreateService
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)


def create_environment(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    project = Project(name=f"Project-{uuid.uuid4()}")
    project_repository.save(project)

    environment = Environment(
        project_id=project.id,
        name="production",
    )
    environment_repository.save(environment)

    return environment


def test_create_service_persists_service(session):
    environment = create_environment(session)

    environment_repository = SqlAlchemyEnvironmentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)

    use_case = CreateService(
        environment_repository,
        service_repository,
    )

    service = use_case.execute(
        environment_id=environment.id,
        name="API",
    )

    stored_service = service_repository.get_by_id(service.id)

    assert stored_service is not None
    assert stored_service.id == service.id
    assert stored_service.environment_id == environment.id
    assert stored_service.name == "API"
    assert stored_service.repository_url is None


def test_create_service_normalizes_name(session):
    environment = create_environment(session)

    use_case = CreateService(
        SqlAlchemyEnvironmentRepository(session),
        SqlAlchemyServiceRepository(session),
    )

    service = use_case.execute(
        environment_id=environment.id,
        name="  API  ",
    )

    assert service.name == "API"


def test_create_service_rejects_unknown_environment(session):
    use_case = CreateService(
        SqlAlchemyEnvironmentRepository(session),
        SqlAlchemyServiceRepository(session),
    )

    with pytest.raises(EnvironmentNotFoundError):
        use_case.execute(
            environment_id=uuid.uuid4(),
            name="API",
        )


def test_create_service_persists_repository_url(session):
    environment = create_environment(session)

    use_case = CreateService(
        SqlAlchemyEnvironmentRepository(session),
        SqlAlchemyServiceRepository(session),
    )

    service = use_case.execute(
        environment_id=environment.id,
        name="API",
    )
    service.update_repository_url("https://github.com/example/api")

    service_repository = SqlAlchemyServiceRepository(session)
    service_repository.save(service)

    stored_service = service_repository.get_by_id(service.id)

    assert stored_service is not None
    assert stored_service.repository_url == "https://github.com/example/api"