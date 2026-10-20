from uuid import UUID

from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.ports.deployment_repository import DeploymentRepository
from nexus.domain.deployments.deployment import Deployment


class RetryFailedDeployment:
    def __init__(self, repository: DeploymentRepository) -> None:
        self.repository = repository

    def execute(self, deployment_id: UUID) -> Deployment:
        deployment = self.repository.get_by_id(deployment_id)

        if deployment is None:
            raise DeploymentNotFoundError()

        deployment.retry()

        self.repository.save(deployment)

        return deployment