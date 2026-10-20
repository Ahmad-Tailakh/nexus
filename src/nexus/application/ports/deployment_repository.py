from typing import Protocol
from uuid import UUID

from nexus.domain.deployments.deployment import Deployment


class DeploymentRepository(Protocol):

    def save(self, deployment: Deployment) -> None:
        ...

    def get_by_id(self, deployment_id: UUID) -> Deployment | None:
        ...

    def list_by_service_id(self, service_id: UUID) -> list[Deployment]:
        ...

    def delete(self, deployment_id: UUID) -> None:
        ...