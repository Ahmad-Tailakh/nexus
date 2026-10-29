from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexus.application.ports.project_repository import ProjectRepository
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.models import ProjectModel


class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def exists_by_name(self, name: str) -> bool:
        statement = (
            select(ProjectModel.id)
            .where(ProjectModel.name == name)
            .limit(1)
        )

        return self.session.execute(statement).scalar_one_or_none() is not None

    def get_by_id(self, project_id: UUID) -> Project | None:
        model = self.session.get(ProjectModel, project_id)

        if model is None:
            return None

        return self._to_domain(model)

    def save(self, project: Project) -> None:
        model = self.session.get(ProjectModel, project.id)

        if model is None:
            model = self._to_model(project)
            self.session.add(model)
        else:
            model.name = project.name
            model.description = project.description
            model.updated_at = project.updated_at

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def list_all(self) -> list[Project]:
        statement = select(ProjectModel).order_by(ProjectModel.created_at)

        models = self.session.execute(statement).scalars().all()

        return [self._to_domain(model) for model in models]

    def delete(self, project_id: UUID) -> None:
        model = self.session.get(ProjectModel, project_id)

        if model is None:
            return

        self.session.delete(model)

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _to_domain(model: ProjectModel) -> Project:
        project = Project(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

        project.updated_at = model.updated_at

        return project

    @staticmethod
    def _to_model(project: Project) -> ProjectModel:
        return ProjectModel(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )