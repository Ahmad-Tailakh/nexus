import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexus.infrastructure.database.base import Base


class ProjectModel(Base):
    """SQLAlchemy persistence model for projects."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )