from uuid import UUID

from nexus.application.ports.service_repository import ServiceRepository
from nexus.domain.services.service import Service


class ListServices:
    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    def execute(self, environment_id: UUID) -> list[Service]:
        return self.repository.list_by_environment_id(environment_id)