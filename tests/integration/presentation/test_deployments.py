import uuid

import pytest

from nexus.domain.deployments.status import DeploymentStatus
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
from nexus.application.deployments.create_deployment import CreateDeployment
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



def create_service(session):
    project = Project(name=f"Project-{uuid.uuid4()}")
    SqlAlchemyProjectRepository(session).save(project)

    environment = Environment(
        project_id=project.id,
        name="production",
    )
    SqlAlchemyEnvironmentRepository(session).save(environment)

    service = Service(
        environment_id=environment.id,
        name="API",
    )
    SqlAlchemyServiceRepository(session).save(service)

    return service


def create_failed_deployment(session):
    service = create_service(session)

    repository = SqlAlchemyDeploymentRepository(session)
    deployment = CreateDeployment(
        SqlAlchemyServiceRepository(session),
        repository,
    ).execute(service_id=service.id)

    deployment.start()
    deployment.fail()
    repository.save(deployment)

    return deployment

def test_create_deployment_returns_created_response(client, session):
    service = create_service(session)

    print("REQUEST AUTH HEADER:", client.headers.get("Authorization"))

    response = client.post(
        "/deployments",
        json={"service_id": str(service.id)},
    )

    assert response.status_code == 201

    body = response.json()
    assert body["service_id"] == str(service.id)
    assert body["status"] == DeploymentStatus.PENDING.value
    assert "id" in body

    stored = SqlAlchemyDeploymentRepository(session).get_by_id(
        uuid.UUID(body["id"])
    )
    assert stored is not None
    assert stored.service_id == service.id


def test_get_deployment_returns_deployment(client, session):
    service = create_service(session)

    create_response = client.post(
        "/deployments",
        json={"service_id": str(service.id)},
    )
    deployment_id = create_response.json()["id"]

    response = client.get(f"/deployments/{deployment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == deployment_id
    assert response.json()["service_id"] == str(service.id)
    assert response.json()["status"] == DeploymentStatus.PENDING.value


def test_get_deployment_returns_not_found_for_unknown_id(client):
    response = client.get(f"/deployments/{uuid.uuid4()}")

    assert response.status_code == 404


def test_retry_deployment_returns_conflict_when_not_failed(client, session):
    service = create_service(session)

    create_response = client.post(
        "/deployments",
        json={"service_id": str(service.id)},
    )
    deployment_id = create_response.json()["id"]

    response = client.post(f"/deployments/{deployment_id}/retry")

    assert response.status_code == 409


def test_retry_failed_deployment_returns_pending_status(client, session):
    deployment = create_failed_deployment(session)

    response = client.post(
        f"/deployments/{deployment.id}/retry"
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(deployment.id)
    assert response.json()["status"] == DeploymentStatus.PENDING.value

    stored = SqlAlchemyDeploymentRepository(session).get_by_id(
        deployment.id
    )
    assert stored is not None
    assert stored.status == DeploymentStatus.PENDING


def test_retry_deployment_returns_not_found_for_unknown_id(client):
    response = client.post(
        f"/deployments/{uuid.uuid4()}/retry"
    )

    assert response.status_code == 404


def test_delete_deployment_returns_no_content(client, session):
    service = create_service(session)

    create_response = client.post(
        "/deployments",
        json={"service_id": str(service.id)},
    )
    deployment_id = uuid.UUID(create_response.json()["id"])

    response = client.delete(f"/deployments/{deployment_id}")

    assert response.status_code == 204
    assert response.content == b""

    stored = SqlAlchemyDeploymentRepository(session).get_by_id(
        deployment_id
    )
    assert stored is None


def test_delete_deployment_returns_not_found_for_unknown_id(client):
    response = client.delete(
        f"/deployments/{uuid.uuid4()}"
    )

    assert response.status_code == 404
