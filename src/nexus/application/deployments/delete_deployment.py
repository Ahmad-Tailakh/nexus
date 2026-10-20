from uuid import UUID

from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.ports.deployment_repository import DeploymentRepository


class DeleteDeployment:
    def __init__(self, repository: DeploymentRepository) -> None:
        self.repository = repository

    def execute(self, deployment_id: UUID) -> None:
        deployment = self.repository.get_by_id(deployment_id)

        if deployment is None:
            raise DeploymentNotFoundError()

        self.repository.delete(deployment_id)