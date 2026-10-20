from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .exceptions import (
    InvalidDeploymentServiceIdError,
    InvalidDeploymentTransitionError,
)
from .status import DeploymentStatus


@dataclass(kw_only=True)
class Deployment:
    id: UUID = field(default_factory=uuid4)
    service_id: UUID
    status: DeploymentStatus = field(
        default=DeploymentStatus.PENDING,
        init=False,
    )
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.service_id, UUID):
            raise InvalidDeploymentServiceIdError()

    def start(self) -> None:
        if self.status != DeploymentStatus.PENDING:
            raise InvalidDeploymentTransitionError()

        self.status = DeploymentStatus.RUNNING
        self._touch()

    def succeed(self) -> None:
        if self.status != DeploymentStatus.RUNNING:
            raise InvalidDeploymentTransitionError()

        self.status = DeploymentStatus.SUCCEEDED
        self._touch()

    def fail(self) -> None:
        if self.status != DeploymentStatus.RUNNING:
            raise InvalidDeploymentTransitionError()

        self.status = DeploymentStatus.FAILED
        self._touch()

    def retry(self) -> None:
        if self.status != DeploymentStatus.FAILED:
            raise InvalidDeploymentTransitionError()

        self.status = DeploymentStatus.PENDING
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)