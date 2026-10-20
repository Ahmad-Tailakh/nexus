from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
from nexus.presentation.dependencies import get_db_session

router = APIRouter(prefix="/deployments", tags=["Deployments"])


class CreateDeploymentRequest(BaseModel):
    service_id: UUID


class RetryDeploymentRequest(BaseModel):
    pass


def serialize_deployment(deployment) -> dict[str, str]:
    return {
        "id": str(deployment.id),
        "service_id": str(deployment.service_id),
        "environment_id": str(deployment.environment_id),
        "status": deployment.status.value
        if hasattr(deployment.status, "value")
        else str(deployment.status),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_deployment(
    request: CreateDeploymentRequest,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
    deployment_repository = SqlAlchemyDeploymentRepository(session)
    service_repository = SqlAlchemyServiceRepository(session)

    deployment = CreateDeployment(
        service_repository,
        deployment_repository,
    ).execute(service_id=request.service_id)

    return serialize_deployment(deployment)


@router.get("/{deployment_id}")
def get_deployment(
    deployment_id: UUID,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
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


@router.post("/{deployment_id}/retry")
def retry_failed_deployment(
    deployment_id: UUID,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
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

    return serialize_deployment(deployment)