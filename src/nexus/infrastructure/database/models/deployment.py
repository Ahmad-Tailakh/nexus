# src/nexus/infrastructure/database/models/deployment.py

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexus.infrastructure.database.base import Base


class DeploymentModel(Base):
    """SQLAlchemy persistence model for deployments."""

    __tablename__ = "deployments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )