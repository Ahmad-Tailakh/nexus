from fastapi.testclient import TestClient
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.domain.projects.project import Project
from nexus.presentation.app import app
from nexus.presentation.routers.projects import get_db_session

def test_list_projects_returns_projects(session):
    def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        repository = SqlAlchemyProjectRepository(session)
        repository.save(
            Project(
                name="Nexus",
                description="Backend project",
            )
        )

        client = TestClient(app)
        response = client.get("/projects")

        assert response.status_code == 200

        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == "Nexus"
        assert projects[0]["description"] == "Backend project"
        assert "id" in projects[0]
    finally:
        app.dependency_overrides.clear()