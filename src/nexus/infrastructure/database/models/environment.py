import uuid

from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from nexus.infrastructure.database.base import Base


class EnvironmentModel(Base):
    """SQLAlchemy persistence model for environments."""

    __tablename__ = "environments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
