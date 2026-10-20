from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from nexus.application.projects.create_project import CreateProject
from nexus.application.projects.delete_project import DeleteProject
from nexus.application.projects.exceptions import (
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
)
from nexus.application.projects.get_project import GetProject
from nexus.application.projects.list_projects import ListProjects
from nexus.application.projects.rename_project import RenameProject
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.presentation.dependencies import get_db_session

router = APIRouter(prefix="/projects", tags=["Projects"])


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class RenameProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


def serialize_project(project) -> dict[str, str | None]:
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
    }


@router.get("")
def list_projects(
    session: Session = Depends(get_db_session),
) -> list[dict[str, str | None]]:
    repository = SqlAlchemyProjectRepository(session)
    projects = ListProjects(repository).execute()

    return [serialize_project(project) for project in projects]


@router.post("", status_code=status.HTTP_201_CREATED)
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
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return serialize_project(project)


@router.get("/{project_id}")
def get_project(
    project_id: UUID,
    session: Session = Depends(get_db_session),
) -> dict[str, str | None]:
    repository = SqlAlchemyProjectRepository(session)

    try:
        project = GetProject(repository).execute(project_id=project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_project(project)


@router.patch("/{project_id}")
def rename_project(
    project_id: UUID,
    request: RenameProjectRequest,
    session: Session = Depends(get_db_session),
) -> dict[str, str | None]:
    repository = SqlAlchemyProjectRepository(session)

    try:
        project = RenameProject(repository).execute(
            project_id=project_id,
            name=request.name,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ProjectNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return serialize_project(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    session: Session = Depends(get_db_session),
) -> None:
    repository = SqlAlchemyProjectRepository(session)

    try:
        DeleteProject(repository).execute(project_id=project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc