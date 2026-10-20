from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexus.domain.services.service import Service
from nexus.infrastructure.database.models.service import ServiceModel


class SqlAlchemyServiceRepository:
    """SQLAlchemy implementation of the service repository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, service: Service) -> None:
        model = self.session.get(ServiceModel, service.id)

        if model is None:
            model = ServiceModel(
                id=service.id,
                environment_id=service.environment_id,
                name=service.name,
                repository_url=service.repository_url,
            )
            self.session.add(model)
        else:
            model.environment_id = service.environment_id
            model.name = service.name
            model.repository_url = service.repository_url

        self.session.commit()

    def exists_by_environment_id(self, environment_id: UUID) -> bool:
        statement = (
            select(ServiceModel.id)
            .where(ServiceModel.environment_id == environment_id)
            .limit(1)
        )
        return self.session.execute(statement).first() is not None

    def get_by_id(self, service_id: UUID) -> Service | None:
        model = self.session.get(ServiceModel, service_id)

        if model is None:
            return None

        return self._to_domain(model)

    def list_by_environment_id(self, environment_id: UUID) -> list[Service]:
        statement = (
            select(ServiceModel)
            .where(ServiceModel.environment_id == environment_id)
            .order_by(ServiceModel.name)
        )
        models = self.session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def delete(self, service_id: UUID) -> None:
        model = self.session.get(ServiceModel, service_id)

        if model is not None:
            self.session.delete(model)
            self.session.commit()

    @staticmethod
    def _to_domain(model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            environment_id=model.environment_id,
            name=model.name,
            repository_url=model.repository_url,
        )