from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from nexus.application.projects.create_project import CreateProject
from nexus.application.projects.delete_project import DeleteProject
from nexus.application.projects.exceptions import (
    ProjectHasEnvironmentsError,
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
)
from nexus.application.projects.get_project import GetProject
from nexus.application.projects.list_projects import ListProjects
from nexus.application.projects.rename_project import RenameProject
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.presentation.dependencies.db import get_db_session
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)




class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Project name must not be blank.")
        return value


class RenameProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None


def serialize_project(project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
def list_projects(
    session: Session = Depends(get_db_session),
) -> list[ProjectResponse]:
    repository = SqlAlchemyProjectRepository(session)
    projects = ListProjects(repository).execute()

    return [serialize_project(project) for project in projects]


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    request: CreateProjectRequest,
    session: Session = Depends(get_db_session),
) -> ProjectResponse:
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


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: UUID,
    session: Session = Depends(get_db_session),
) -> ProjectResponse:
    repository = SqlAlchemyProjectRepository(session)

    try:
        project = GetProject(repository).execute(
            project_id=project_id,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_project(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
def rename_project(
    project_id: UUID,
    request: RenameProjectRequest,
    session: Session = Depends(get_db_session),
) -> ProjectResponse:
    repository = SqlAlchemyProjectRepository(session)

    try:
        project = RenameProject(repository).execute(
            project_id=project_id,
            new_name=request.name,
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
    project_repository = SqlAlchemyProjectRepository(session)
    environment_repository = SqlAlchemyEnvironmentRepository(session)

    try:
        DeleteProject(
            project_repository=project_repository,
            environment_repository=environment_repository,
        ).execute(project_id=project_id)

    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ProjectHasEnvironmentsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc