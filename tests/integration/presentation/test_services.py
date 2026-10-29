import uuid

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


def create_environment(session, name="development"):
    project = Project(name=f"Project-{uuid.uuid4()}")
    SqlAlchemyProjectRepository(session).save(project)

    environment = Environment(
        project_id=project.id,
        name=name,
    )
    SqlAlchemyEnvironmentRepository(session).save(environment)

    return environment


def test_create_service_returns_created_response(client, session):
    environment = create_environment(session)

    response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "api"
    assert body["environment_id"] == str(environment.id)
    assert body["repository_url"] is None
    assert "id" in body


def test_create_service_with_repository_url(client, session):
    environment = create_environment(session)
    repository_url = "https://github.com/example/api"

    response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
            "repository_url": repository_url,
        },
    )

    assert response.status_code == 201
    assert response.json()["repository_url"] == repository_url


def test_create_service_returns_not_found_for_unknown_environment(client):
    response = client.post(
        "/services",
        json={
            "environment_id": str(uuid.uuid4()),
            "name": "api",
        },
    )

    assert response.status_code == 404


def test_create_service_rejects_empty_name(client, session):
    environment = create_environment(session)

    response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "",
        },
    )

    assert response.status_code == 422


def test_create_service_rejects_invalid_environment_id(client):
    response = client.post(
        "/services",
        json={
            "environment_id": "not-a-uuid",
            "name": "api",
        },
    )

    assert response.status_code == 422


def test_list_services_returns_services(client, session):
    environment = create_environment(session)

    client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
        },
    )
    client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "worker",
        },
    )

    response = client.get(
        "/services",
        params={"environment_id": str(environment.id)},
    )

    assert response.status_code == 200
    assert {service["name"] for service in response.json()} == {
        "api",
        "worker",
    }


def test_list_services_rejects_missing_environment_id(client):
    response = client.get("/services")

    assert response.status_code == 422


def test_list_services_returns_empty_list_for_environment_without_services(
    client, session
):
    environment = create_environment(session)

    response = client.get(
        "/services",
        params={"environment_id": str(environment.id)},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_service_returns_service(client, session):
    environment = create_environment(session)

    create_response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
        },
    )
    service_id = create_response.json()["id"]

    response = client.get(f"/services/{service_id}")

    assert response.status_code == 200
    assert response.json()["id"] == service_id
    assert response.json()["name"] == "api"


def test_get_service_returns_not_found_for_unknown_id(client):
    response = client.get(f"/services/{uuid.uuid4()}")

    assert response.status_code == 404


def test_update_repository_url_updates_service(client, session):
    environment = create_environment(session)

    create_response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
        },
    )
    service_id = create_response.json()["id"]
    repository_url = "https://github.com/example/api"

    response = client.patch(
        f"/services/{service_id}/repository-url",
        json={"repository_url": repository_url},
    )

    assert response.status_code == 200
    assert response.json()["repository_url"] == repository_url

    stored = SqlAlchemyServiceRepository(session).get_by_id(
        uuid.UUID(service_id)
    )
    assert stored is not None
    assert stored.repository_url == repository_url


def test_update_repository_url_returns_not_found_for_unknown_service(client):
    response = client.patch(
        f"/services/{uuid.uuid4()}/repository-url",
        json={"repository_url": "https://github.com/example/api"},
    )

    assert response.status_code == 404


def test_update_repository_url_rejects_empty_url(client):
    response = client.patch(
        f"/services/{uuid.uuid4()}/repository-url",
        json={"repository_url": ""},
    )

    assert response.status_code == 422


def test_delete_service_returns_no_content(client, session):
    environment = create_environment(session)

    create_response = client.post(
        "/services",
        json={
            "environment_id": str(environment.id),
            "name": "api",
        },
    )
    service_id = uuid.UUID(create_response.json()["id"])

    response = client.delete(f"/services/{service_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert SqlAlchemyServiceRepository(session).get_by_id(service_id) is None


def test_delete_service_returns_not_found_for_unknown_id(client):
    response = client.delete(f"/services/{uuid.uuid4()}")

    assert response.status_code == 404
