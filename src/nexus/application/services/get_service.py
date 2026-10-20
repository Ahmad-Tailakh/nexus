from uuid import UUID

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.services.service import Service


class GetService:
    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    def execute(self, service_id: UUID) -> Service:
        service = self.repository.get_by_id(service_id)

        if service is None:
            raise ServiceNotFoundError()

        return service