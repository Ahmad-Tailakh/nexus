# tests/integration/infrastructure/database/repositories/test_deployment_repository.py

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from nexus.domain.deployments.deployment import Deployment
from nexus.domain.deployments.status import DeploymentStatus
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
from nexus.infrastructure.database.base import Base
from nexus.infrastructure.database.repositories.deployment_repository import (
    SqlAlchemyDeploymentRepository,
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
def setup_deployment(session):
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)
    deployment_repository = SqlAlchemyDeploymentRepository(session)

    project = Project(name="Test Project")
    project_repository.save(project)

    environment = Environment(
        project_id=project.id,
        name="Test Environment",
    )
    environment_repository.save(environment)

    service = Service(
        environment_id=environment.id,
        name="Test Service",
    )
    service_repository.save(service)

    deployment = Deployment(service_id=service.id)

    return service, deployment, deployment_repository


def test_save_and_get_by_id(setup_deployment):
    _, deployment, repository = setup_deployment

    repository.save(deployment)

    result = repository.get_by_id(deployment.id)

    assert result is not None
    assert result.id == deployment.id
    assert result.service_id == deployment.service_id
    assert result.status == DeploymentStatus.PENDING
    assert result.created_at == deployment.created_at
    assert result.updated_at == deployment.updated_at


def test_get_by_id_returns_none_when_not_found(setup_deployment):
    _, _, repository = setup_deployment

    assert repository.get_by_id(uuid.uuid4()) is None


def test_list_by_service_id_returns_deployments(setup_deployment):
    service, deployment, repository = setup_deployment

    repository.save(deployment)

    second_deployment = Deployment(service_id=service.id)
    repository.save(second_deployment)

    result = repository.list_by_service_id(service.id)

    assert len(result) == 2
    assert {item.id for item in result} == {
        deployment.id,
        second_deployment.id,
    }


def test_save_updates_deployment_status(setup_deployment):
    _, deployment, repository = setup_deployment

    repository.save(deployment)

    deployment.start()
    deployment.succeed()
    repository.save(deployment)

    result = repository.get_by_id(deployment.id)

    assert result is not None
    assert result.status == DeploymentStatus.SUCCEEDED


def test_delete_removes_deployment(setup_deployment):
    _, deployment, repository = setup_deployment

    repository.save(deployment)
    repository.delete(deployment.id)

    assert repository.get_by_id(deployment.id) is None


def test_delete_nonexistent_deployment_does_not_raise(setup_deployment):
    _, _, repository = setup_deployment

    repository.delete(uuid.uuid4())