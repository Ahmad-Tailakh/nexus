from uuid import UUID

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError


class DeleteService:
    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    def execute(self, service_id: UUID) -> None:
        service = self.repository.get_by_id(service_id)

        if service is None:
            raise ServiceNotFoundError()

        self.repository.delete(service_id)