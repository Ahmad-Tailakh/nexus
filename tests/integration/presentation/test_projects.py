import uuid

import pytest


from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def create_project(session, name=None, description=None):
    project = Project(
        name=name or f"Project-{uuid.uuid4()}",
        description=description,
    )
    SqlAlchemyProjectRepository(session).save(project)
    return project


def create_environment(session, project_id, name="development"):
    environment = Environment(
        project_id=project_id,
        name=name,
    )
    SqlAlchemyEnvironmentRepository(session).save(environment)
    return environment


def test_list_projects_returns_projects(client, session):
    create_project(session, "Nexus", "Backend project")

    response = client.get("/projects")

    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "Nexus"
    assert projects[0]["description"] == "Backend project"
    assert "id" in projects[0]


def test_create_project_returns_created_response(client):
    response = client.post(
        "/projects",
        json={"name": "Nexus", "description": "Backend project"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Nexus"
    assert body["description"] == "Backend project"
    assert "id" in body


def test_create_project_without_description(client):
    response = client.post("/projects", json={"name": "Nexus"})

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_project_returns_conflict_for_duplicate_name(client):
    client.post("/projects", json={"name": "Nexus"})

    response = client.post("/projects", json={"name": "Nexus"})

    assert response.status_code == 409


@pytest.mark.parametrize("name", ["", "   "])
def test_create_project_rejects_invalid_name(client, name):
    response = client.post("/projects", json={"name": name})

    assert response.status_code == 422


def test_get_project_returns_project(client, session):
    project = create_project(session, "Nexus", "Backend project")

    response = client.get(f"/projects/{project.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(project.id),
        "name": "Nexus",
        "description": "Backend project",
    }


def test_get_project_returns_not_found_for_unknown_id(client):
    response = client.get(f"/projects/{uuid.uuid4()}")

    assert response.status_code == 404


def test_rename_project_updates_name(client, session):
    project = create_project(session, "Nexus")

    response = client.patch(
        f"/projects/{project.id}",
        json={"name": "Nexus Platform"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Nexus Platform"

    stored = SqlAlchemyProjectRepository(session).get_by_id(project.id)
    assert stored is not None
    assert stored.name == "Nexus Platform"


def test_rename_project_returns_not_found_for_unknown_id(client):
    response = client.patch(
        f"/projects/{uuid.uuid4()}",
        json={"name": "Nexus Platform"},
    )

    assert response.status_code == 404


def test_rename_project_returns_conflict_for_duplicate_name(
    client, session
):
    project = create_project(session, "Nexus")
    create_project(session, "Platform")

    response = client.patch(
        f"/projects/{project.id}",
        json={"name": "Platform"},
    )

    assert response.status_code == 409


def test_delete_project_returns_no_content(client, session):
    project = create_project(session)

    response = client.delete(f"/projects/{project.id}")

    assert response.status_code == 204
    assert response.content == b""
    assert SqlAlchemyProjectRepository(session).get_by_id(project.id) is None


def test_delete_project_returns_not_found_for_unknown_id(client):
    response = client.delete(f"/projects/{uuid.uuid4()}")

    assert response.status_code == 404


def test_delete_project_returns_conflict_when_environments_exist(
    client, session
):
    project = create_project(session)
    create_environment(session, project.id)

    response = client.delete(f"/projects/{project.id}")

    assert response.status_code == 409
    assert SqlAlchemyProjectRepository(session).get_by_id(project.id) is not None
