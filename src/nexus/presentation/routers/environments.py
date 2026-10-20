from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from nexus.application.environments.create_environment import CreateEnvironment
from nexus.application.environments.delete_environment import DeleteEnvironment
from nexus.application.environments.exceptions import (
    EnvironmentNotFoundError,
)
from nexus.application.environments.get_environment import GetEnvironment
from nexus.application.environments.list_environments import ListEnvironments
from nexus.application.environments.rename_environment import RenameEnvironment
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.presentation.dependencies import get_db_session

router = APIRouter(prefix="/environments", tags=["Environments"])


class CreateEnvironmentRequest(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=255)


class RenameEnvironmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


def serialize_environment(environment) -> dict[str, str]:
    return {
        "id": str(environment.id),
        "project_id": str(environment.project_id),
        "name": environment.name,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_environment(
    request: CreateEnvironmentRequest,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
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
    except Exception as exc:
        from nexus.application.environments.exceptions import (
            EnvironmentAlreadyExistsError,
        )

        if isinstance(exc, EnvironmentAlreadyExistsError):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise

    return serialize_environment(environment)


@router.get("")
def list_environments(
    project_id: UUID,
    session: Session = Depends(get_db_session),
) -> list[dict[str, str]]:
    repository = SqlAlchemyEnvironmentRepository(session)
    environments = ListEnvironments(repository).execute(
        project_id=project_id,
    )
    return [serialize_environment(environment) for environment in environments]


@router.get("/{environment_id}")
def get_environment(
    environment_id: UUID,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
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


@router.patch("/{environment_id}")
def rename_environment(
    environment_id: UUID,
    request: RenameEnvironmentRequest,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
    repository = SqlAlchemyEnvironmentRepository(session)

    try:
        environment = RenameEnvironment(repository).execute(
            environment_id=environment_id,
            name=request.name,
        )
    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_environment(environment)


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    environment_id: UUID,
    session: Session = Depends(get_db_session),
) -> None:
    repository = SqlAlchemyEnvironmentRepository(session)

    try:
        DeleteEnvironment(repository).execute(
            environment_id=environment_id,
        )
    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc