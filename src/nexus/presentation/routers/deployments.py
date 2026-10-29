from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from nexus.application.deployments.create_deployment import CreateDeployment
from nexus.application.deployments.delete_deployment import DeleteDeployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.deployments.get_deployment import GetDeployment
from nexus.application.deployments.retry_failed_deployment import (
    RetryFailedDeployment,
)
from nexus.infrastructure.database.repositories.deployment_repository import (
    SqlAlchemyDeploymentRepository,
)
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)
from nexus.domain.deployments.exceptions import InvalidDeploymentTransitionError
from nexus.presentation.dependencies.db import get_db_session


router = APIRouter(
    prefix="/deployments",
    tags=["Deployments"],
)


class CreateDeploymentRequest(BaseModel):
    service_id: UUID


class DeploymentResponse(BaseModel):
    id: UUID
    service_id: UUID
    status: str


def serialize_deployment(deployment) -> DeploymentResponse:
    deployment_status = (
        deployment.status.value
        if hasattr(deployment.status, "value")
        else str(deployment.status)
    )

    return DeploymentResponse(
        id=deployment.id,
        service_id=deployment.service_id,
        status=deployment_status,
    )

@router.post(
    "",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_deployment(
    request: CreateDeploymentRequest,
    session: Session = Depends(get_db_session),
) -> DeploymentResponse:
    deployment_repository = SqlAlchemyDeploymentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)

    deployment = CreateDeployment(
        service_repository,
        deployment_repository,
    ).execute(
        service_id=request.service_id,
    )

    return serialize_deployment(deployment)


@router.get(
    "/{deployment_id}",
    response_model=DeploymentResponse,
)
def get_deployment(
    deployment_id: UUID,
    session: Session = Depends(get_db_session),
) -> DeploymentResponse:
    repository = SqlAlchemyDeploymentRepository(session)

    try:
        deployment = GetDeployment(repository).execute(
            deployment_id=deployment_id,
        )
    except DeploymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return serialize_deployment(deployment)


@router.post(
    "/{deployment_id}/retry",
    response_model=DeploymentResponse,
)
def retry_failed_deployment(
    deployment_id: UUID,
    session: Session = Depends(get_db_session),
) -> DeploymentResponse:
    repository = SqlAlchemyDeploymentRepository(session)

    try:
        deployment = RetryFailedDeployment(repository).execute(
            deployment_id=deployment_id,
        )
    except DeploymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidDeploymentTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return serialize_deployment(deployment)

@router.delete(
    "/{deployment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_deployment(
    deployment_id: UUID,
    session: Session = Depends(get_db_session),
) -> None:
    repository = SqlAlchemyDeploymentRepository(session)

    try:
        DeleteDeployment(repository).execute(
            deployment_id=deployment_id,
        )
    except DeploymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc