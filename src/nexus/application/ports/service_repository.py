from typing import Protocol
from uuid import UUID

from nexus.domain.services.service import Service


class ServiceRepository(Protocol):

    def save(self, service: Service) -> None:
        ...

    def exists_by_environment_id(self,environment_id: UUID,) -> bool:
        ...

    def get_by_id(self, service_id: UUID) -> Service | None:
        ...

    def list_by_environment_id(self,environment_id: UUID) -> list[Service]:
        ...

    def delete(self, service_id: UUID) -> None:
        ...