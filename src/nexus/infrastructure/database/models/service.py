
import uuid

from sqlalchemy import ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexus.infrastructure.database.base import Base


class ServiceModel(Base):
    """SQLAlchemy persistence model for services."""

    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("environments.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    repository_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )