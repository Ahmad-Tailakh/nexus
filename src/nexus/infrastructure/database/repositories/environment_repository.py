from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.domain.environments.environment import Environment
from nexus.infrastructure.database.models import EnvironmentModel


class SqlAlchemyEnvironmentRepository(EnvironmentRepository):
    """SQLAlchemy repository for environments."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, environment: Environment) -> None:
        model = self.session.get(EnvironmentModel, environment.id)

        if model is None:
            model = EnvironmentModel(id=environment.id)
            self.session.add(model)

        model.project_id = environment.project_id
        model.name = environment.name

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, environment_id: UUID) -> Environment | None:
        model = self.session.get(EnvironmentModel, environment_id)

        if model is None:
            return None

        return self._to_domain(model)

    def exists_by_name(self, project_id: UUID, name: str) -> bool:
        statement = select(
            EnvironmentModel.id
        ).where(
            EnvironmentModel.project_id == project_id,
            EnvironmentModel.name == name,
        ).limit(1)

        return self.session.scalar(statement) is not None

    def delete(self, environment: Environment) -> None:
        model = self.session.get(EnvironmentModel, environment.id)

        if model is not None:
            self.session.delete(model)
            self.session.commit()

    def list_by_project_id(self, project_id: UUID) -> list[Environment]:
        statement = (
            select(EnvironmentModel)
            .where(EnvironmentModel.project_id == project_id)
            .order_by(EnvironmentModel.name)
        )

        models = self.session.execute(statement).scalars().all()

        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: EnvironmentModel) -> Environment:
        return Environment(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
        )