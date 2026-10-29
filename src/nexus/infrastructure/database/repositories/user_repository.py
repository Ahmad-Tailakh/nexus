
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexus.application.ports.user_repository import UserRepository
from nexus.domain.users.user import User
from nexus.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self.session.get(UserModel, user_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_email(self, email: str) -> User | None:
        statement = select(UserModel).where(
            UserModel.email == email.strip().lower()
        )
        model = self.session.execute(statement).scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    def save(self, user: User) -> None:
        model = self.session.get(UserModel, user.id)

        if model is None:
            model = self._to_model(user)
            self.session.add(model)
        else:
            model.email = user.email
            model.password_hash = user.password_hash
            model.updated_at = user.updated_at

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
