# src/nexus/infrastructure/database/repositories/deployment_repository.py

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from nexus.domain.deployments.deployment import Deployment
from nexus.domain.deployments.status import DeploymentStatus
from nexus.infrastructure.database.models.deployment import DeploymentModel


class SqlAlchemyDeploymentRepository:
    """SQLAlchemy implementation of the deployment repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, deployment: Deployment) -> None:
        model = self.session.get(DeploymentModel, deployment.id)

        if model is None:
            model = DeploymentModel(
                id=deployment.id,
                service_id=deployment.service_id,
                status=deployment.status.value,
                created_at=deployment.created_at,
                updated_at=deployment.updated_at,
            )
            self.session.add(model)
        else:
            model.service_id = deployment.service_id
            model.status = deployment.status.value
            model.created_at = deployment.created_at
            model.updated_at = deployment.updated_at

        self.session.commit()

    def get_by_id(self, deployment_id: UUID) -> Deployment | None:
        model = self.session.get(DeploymentModel, deployment_id)

        if model is None:
            return None

        return self._to_domain(model)

    def list_by_service_id(self, service_id: UUID) -> list[Deployment]:
        statement = (
            select(DeploymentModel)
            .where(DeploymentModel.service_id == service_id)
            .order_by(DeploymentModel.created_at.desc())
        )
        models = self.session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def delete(self, deployment_id: UUID) -> None:
        model = self.session.get(DeploymentModel, deployment_id)

        if model is not None:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: DeploymentModel) -> Deployment:
        def ensure_utc(value: datetime) -> datetime:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        deployment = Deployment(
            id=model.id,
            service_id=model.service_id,
        )
        deployment.status = DeploymentStatus(model.status)
        deployment.created_at = ensure_utc(model.created_at)
        deployment.updated_at = ensure_utc(model.updated_at)

        return deployment