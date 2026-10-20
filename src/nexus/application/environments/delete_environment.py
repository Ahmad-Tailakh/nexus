from uuid import UUID

from nexus.application.environments.exceptions import (
    EnvironmentHasServicesError,
    EnvironmentNotFoundError,
)
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.service_repository import ServiceRepository



class DeleteEnvironment:
    def __init__(
        self,
        environment_repository: EnvironmentRepository,
        service_repository: ServiceRepository,
    ) -> None:
        self.environment_repository = environment_repository
        self.service_repository = service_repository

    def execute(self, environment_id: UUID) -> None:
        environment = self.environment_repository.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        if self.service_repository.exists_by_environment_id(environment_id):
            raise EnvironmentHasServicesError()

        self.environment_repository.delete(environment)