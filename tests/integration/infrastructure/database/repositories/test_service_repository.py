import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
from nexus.infrastructure.database.base import Base
from nexus.infrastructure.database.models import (
    EnvironmentModel,
    ProjectModel,
    ServiceModel,
)
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def repositories(session):
    return (
        SqlAlchemyProjectRepository(session),
        SqlAlchemyEnvironmentRepository(session),
        SqlAlchemyServiceRepository(session),
    )


@pytest.fixture
def service(repositories):
    project_repository, environment_repository, service_repository = repositories

    project = Project(name="Test Project")
    project_repository.save(project)

    environment = Environment(
        project_id=project.id,
        name="Test Environment",
    )
    environment_repository.save(environment)

    return Service(
        environment_id=environment.id,
        name="Test Service",
        repository_url="https://github.com/example/repo",
    )


def test_save_and_get_by_id(repositories, service):
    _, _, repository = repositories

    repository.save(service)

    result = repository.get_by_id(service.id)

    assert result is not None
    assert result.id == service.id
    assert result.environment_id == service.environment_id
    assert result.name == service.name
    assert result.repository_url == service.repository_url


def test_list_by_environment_id_returns_services_ordered_by_name(
    repositories,
    service,
):
    _, _, repository = repositories

    repository.save(service)

    another_service = Service(
        environment_id=service.environment_id,
        name="Another Service",
    )
    repository.save(another_service)

    result = repository.list_by_environment_id(service.environment_id)

    assert [item.name for item in result] == [
        "Another Service",
        "Test Service",
    ]


def test_exists_by_environment_id_returns_true_when_service_exists(
    repositories,
    service,
):
    _, _, repository = repositories

    repository.save(service)

    assert repository.exists_by_environment_id(service.environment_id) is True


def test_exists_by_environment_id_returns_false_when_no_service_exists(
    repositories,
    service,
):
    _, _, repository = repositories

    assert repository.exists_by_environment_id(service.environment_id) is False


def test_get_by_id_returns_none_when_service_does_not_exist(repositories):
    _, _, repository = repositories

    assert repository.get_by_id(uuid.uuid4()) is None


def test_delete_removes_service(repositories, service):
    _, _, repository = repositories

    repository.save(service)
    repository.delete(service.id)

    assert repository.get_by_id(service.id) is None


def test_delete_nonexistent_service_does_not_raise(repositories):
    _, _, repository = repositories

    repository.delete(uuid.uuid4())