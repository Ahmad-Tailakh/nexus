from uuid import UUID

from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.services.service import Service


class UpdateRepositoryUrl:
    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    def execute(
        self,
        service_id: UUID,
        repository_url: str | None,
    ) -> Service:
        service = self.repository.get_by_id(service_id)

        if service is None:
            raise ServiceNotFoundError()

        service.update_repository_url(repository_url)

        self.repository.save(service)

        return service