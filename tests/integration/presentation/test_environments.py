import uuid

import pytest

from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)

from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)


def create_project(session):
    project = Project(name=f"Project-{uuid.uuid4()}")
    SqlAlchemyProjectRepository(session).save(project)
    return project


def create_environment(session, project_id, name="development"):
    environment = Environment(
        project_id=project_id,
        name=name,
    )
    SqlAlchemyEnvironmentRepository(session).save(environment)
    return environment


def create_service(session, environment_id, name="API"):
    service = Service(
        environment_id=environment_id,
        name=name,
    )
    SqlAlchemyServiceRepository(session).save(service)
    return service


def test_create_environment_returns_created_response(client, session):
    project = create_project(session)

    response = client.post(
        "/environments",
        json={
            "project_id": str(project.id),
            "name": "development",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["project_id"] == str(project.id)
    assert body["name"] == "development"
    assert "id" in body


def test_create_environment_returns_conflict_for_duplicate_name(
    client, session
):
    project = create_project(session)
    create_environment(session, project.id, "development")

    response = client.post(
        "/environments",
        json={
            "project_id": str(project.id),
            "name": "development",
        },
    )

    assert response.status_code == 409


def test_list_environments_returns_environments_for_project(
    client, session
):
    project = create_project(session)
    create_environment(session, project.id, "development")
    create_environment(session, project.id, "production")

    response = client.get(
        "/environments",
        params={"project_id": str(project.id)},
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 2
    assert {item["name"] for item in body} == {
        "development",
        "production",
    }
    assert all(
        item["project_id"] == str(project.id)
        for item in body
    )


def test_get_environment_returns_environment(client, session):
    project = create_project(session)
    environment = create_environment(session, project.id)

    response = client.get(f"/environments/{environment.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(environment.id)
    assert response.json()["project_id"] == str(project.id)
    assert response.json()["name"] == "development"


def test_get_environment_returns_not_found_for_unknown_id(client):
    response = client.get(f"/environments/{uuid.uuid4()}")

    assert response.status_code == 404


def test_rename_environment_updates_name(client, session):
    project = create_project(session)
    environment = create_environment(session, project.id)

    response = client.patch(
        f"/environments/{environment.id}",
        json={"name": "production"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "production"

    stored = SqlAlchemyEnvironmentRepository(session).get_by_id(
        environment.id
    )
    assert stored is not None
    assert stored.name == "production"


def test_rename_environment_returns_not_found_for_unknown_id(client):
    response = client.patch(
        f"/environments/{uuid.uuid4()}",
        json={"name": "production"},
    )

    assert response.status_code == 404


def test_rename_environment_returns_conflict_for_duplicate_name(
    client, session
):
    project = create_project(session)
    development = create_environment(
        session, project.id, "development"
    )
    create_environment(session, project.id, "production")

    response = client.patch(
        f"/environments/{development.id}",
        json={"name": "production"},
    )

    assert response.status_code == 409


def test_delete_environment_returns_no_content(client, session):
    project = create_project(session)
    environment = create_environment(session, project.id)

    response = client.delete(f"/environments/{environment.id}")

    assert response.status_code == 204
    assert response.content == b""

    stored = SqlAlchemyEnvironmentRepository(session).get_by_id(
        environment.id
    )
    assert stored is None


def test_delete_environment_returns_not_found_for_unknown_id(client):
    response = client.delete(f"/environments/{uuid.uuid4()}")

    assert response.status_code == 404


def test_delete_environment_returns_conflict_when_services_exist(
    client, session
):
    project = create_project(session)
    environment = create_environment(session, project.id)
    create_service(session, environment.id)

    response = client.delete(f"/environments/{environment.id}")

    assert response.status_code == 409

    stored = SqlAlchemyEnvironmentRepository(session).get_by_id(
        environment.id
    )
    assert stored is not None