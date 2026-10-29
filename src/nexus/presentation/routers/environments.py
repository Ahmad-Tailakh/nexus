from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from nexus.application.environments.create_environment import CreateEnvironment
from nexus.application.environments.delete_environment import DeleteEnvironment
from nexus.application.environments.exceptions import (
    EnvironmentHasServicesError,
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
)
from nexus.application.environments.get_environment import GetEnvironment
from nexus.application.environments.list_environments import ListEnvironments
from nexus.application.environments.rename_environment import RenameEnvironment
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)

from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)

from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.presentation.dependencies.db import get_db_session


router = APIRouter(
    prefix="/environments",
    tags=["Environments"],
)


class CreateEnvironmentRequest(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=255)


class RenameEnvironmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class EnvironmentResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str


def serialize_environment(environment) -> EnvironmentResponse:
    return EnvironmentResponse(
        id=environment.id,
        project_id=environment.project_id,
        name=environment.name,
    )


@router.get(
    "",
    response_model=list[EnvironmentResponse],
    status_code=status.HTTP_200_OK,
)
def list_environments(
    project_id: UUID = Query(...),
    session: Session = Depends(get_db_session),
) -> list[EnvironmentResponse]:
    repository = SqlAlchemyEnvironmentRepository(session)

    environments = ListEnvironments(repository).execute(
        project_id=project_id,
    )

    return [
        serialize_environment(environment)
        for environment in environments
    ]


@router.post(
    "",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_environment(
    request: CreateEnvironmentRequest,
    session: Session = Depends(get_db_session),
) -> EnvironmentResponse:
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)

    try:
        environment = CreateEnvironment(
            project_repository,
            environment_repository,
        ).execute(
            project_id=request.project_id,
            name=request.name,
        )
    except EnvironmentNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return serialize_environment(environment)


@router.get(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_environment(
    environment_id: UUID,
    session: Session = Depends(get_db_session),
) -> EnvironmentResponse:
    repository = SqlAlchemyEnvironmentRepository(session)

    try:
        environment = GetEnvironment(repository).execute(
            environment_id=environment_id,
        )
    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_environment(environment)


@router.patch(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_200_OK,
)
def rename_environment(
    environment_id: UUID,
    request: RenameEnvironmentRequest,
    session: Session = Depends(get_db_session),
) -> EnvironmentResponse:
    repository = SqlAlchemyEnvironmentRepository(session)

    try:
        environment = RenameEnvironment(repository).execute(
            environment_id=environment_id,
            new_name=request.name,
        )
    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EnvironmentNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return serialize_environment(environment)



@router.delete(
    "/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_environment(
    environment_id: UUID,
    session: Session = Depends(get_db_session),
) -> None:
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)

    try:
        DeleteEnvironment(
            environment_repository=environment_repository,
            service_repository=service_repository,
        ).execute(environment_id=environment_id)

    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except EnvironmentHasServicesError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc