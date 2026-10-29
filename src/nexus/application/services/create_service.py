
from uuid import UUID

from nexus.application.environments.exceptions import EnvironmentNotFoundError
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.service_repository import ServiceRepository
from nexus.domain.services.service import Service


class CreateService:
    def __init__(
        self,
        environment_repository: EnvironmentRepository,
        service_repository: ServiceRepository,
    ) -> None:
        self._environment_repository = environment_repository
        self._service_repository = service_repository

    def execute(
        self,
        environment_id: UUID,
        name: str,
        repository_url: str | None = None,
    ) -> Service:
        environment = self._environment_repository.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        service = Service(
            environment_id=environment.id,
            name=name,
            repository_url=repository_url,
        )

        self._service_repository.save(service)

        return service
