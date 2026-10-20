from uuid import UUID

from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.application.ports.service_repository import ServiceRepository
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.deployments.deployment import Deployment


class CreateDeployment:
    def __init__(
        self,
        service_repository: ServiceRepository,
        deployment_repository: DeploymentRepository,
    ) -> None:
        self.service_repository = service_repository
        self.deployment_repository = deployment_repository

    def execute(self, service_id: UUID) -> Deployment:
        service = self.service_repository.get_by_id(service_id)

        if service is None:
            raise ServiceNotFoundError()

        deployment = Deployment(service_id=service_id)

        self.deployment_repository.save(deployment)

        return deployment