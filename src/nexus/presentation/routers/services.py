from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from nexus.application.services.create_service import CreateService
from nexus.application.services.delete_service import DeleteService
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.application.services.get_service import GetService
from nexus.application.services.list_services import ListServices
from nexus.application.services.update_repository_url import UpdateRepositoryUrl
from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)
from nexus.presentation.dependencies.db import get_db_session

from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


class CreateServiceRequest(BaseModel):
    environment_id: UUID
    name: str = Field(min_length=1, max_length=255)
    repository_url: str | None = Field(
        default=None,
        max_length=2048,
    )


class UpdateRepositoryUrlRequest(BaseModel):
    repository_url: str = Field(
        min_length=1,
        max_length=2048,
    )


class ServiceResponse(BaseModel):
    id: UUID
    environment_id: UUID
    name: str
    repository_url: str | None = None


def serialize_service(service) -> ServiceResponse:
    return ServiceResponse(
        id=service.id,
        environment_id=service.environment_id,
        name=service.name,
        repository_url=service.repository_url,
    )


@router.get(
    "",
    response_model=list[ServiceResponse],
    status_code=status.HTTP_200_OK,
)
def list_services(
    environment_id: UUID = Query(...),
    session: Session = Depends(get_db_session),
) -> list[ServiceResponse]:
    repository = SqlAlchemyServiceRepository(session)

    services = ListServices(repository).execute(
        environment_id=environment_id,
    )

    return [serialize_service(service) for service in services]



@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    request: CreateServiceRequest,
    session: Session = Depends(get_db_session),
) -> ServiceResponse:
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)

    try:
        service = CreateService(
            environment_repository=environment_repository,
            service_repository=service_repository,
        ).execute(
            environment_id=request.environment_id,
            name=request.name,
            repository_url=request.repository_url,
        )
    except EnvironmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_service(service)

@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
)
def get_service(
    service_id: UUID,
    session: Session = Depends(get_db_session),
) -> ServiceResponse:
    repository = SqlAlchemyServiceRepository(session)

    try:
        service = GetService(repository).execute(
            service_id=service_id,
        )
    except ServiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_service(service)


@router.patch(
    "/{service_id}/repository-url",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
)
def update_repository_url(
    service_id: UUID,
    request: UpdateRepositoryUrlRequest,
    session: Session = Depends(get_db_session),
) -> ServiceResponse:
    repository = SqlAlchemyServiceRepository(session)

    try:
        service = UpdateRepositoryUrl(repository).execute(
            service_id=service_id,
            repository_url=request.repository_url,
        )
    except ServiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_service(service)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    service_id: UUID,
    session: Session = Depends(get_db_session),
) -> None:
    repository = SqlAlchemyServiceRepository(session)

    try:
        DeleteService(repository).execute(
            service_id=service_id,
        )
    except ServiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
