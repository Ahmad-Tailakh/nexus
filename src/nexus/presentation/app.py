from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from nexus.application.projects.create_project import CreateProject
from nexus.application.projects.exceptions import ProjectNameAlreadyExistsError
from nexus.application.projects.list_projects import ListProjects
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.infrastructure.database.session import SessionFactory

from fastapi import FastAPI

from nexus.presentation.routers import environments, health, projects

app = FastAPI(title="Nexus API")

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(environments.router)


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


def get_db_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/projects")
def list_projects(
    session: Session = Depends(get_db_session),
) -> list[dict[str, str | None]]:
    repository = SqlAlchemyProjectRepository(session)
    projects = ListProjects(repository).execute()

    return [
        {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
        }
        for project in projects
    ]


@app.post("/projects", status_code=201)
def create_project(
    request: CreateProjectRequest,
    session: Session = Depends(get_db_session),
) -> dict[str, str | None]:
    repository = SqlAlchemyProjectRepository(session)

    try:
        project = CreateProject(repository).execute(
            name=request.name,
            description=request.description,
        )
    except ProjectNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="A project with this name already exists.",
        ) from exc

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
    }