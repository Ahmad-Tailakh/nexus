import uuid

import pytest

from nexus.application.deployments.create_deployment import CreateDeployment
from nexus.application.deployments.retry_failed_deployment import RetryFailedDeployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.domain.deployments.status import DeploymentStatus
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
from nexus.infrastructure.database.repositories.deployment_repository import (
    SqlAlchemyDeploymentRepository,
)
from nexus.infrastructure.database.repositories.environment_repository import (
    SqlAlchemyEnvironmentRepository,
)
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from nexus.infrastructure.database.repositories.service_repository import (
    SqlAlchemyServiceRepository,
)


def create_deployment(session):
    project = Project(name=f"Project-{uuid.uuid4()}")
    SqlAlchemyProjectRepository(session).save(project)

    environment = Environment(project_id=project.id, name="production")
    SqlAlchemyEnvironmentRepository(session).save(environment)

    service = Service(environment_id=environment.id, name="API")
    SqlAlchemyServiceRepository(session).save(service)

    service_repository = SqlAlchemyServiceRepository(session)
    deployment_repository = SqlAlchemyDeploymentRepository(session)

    deployment = CreateDeployment(
        service_repository,
        deployment_repository,
    ).execute(service_id=service.id)

    deployment.start()
    deployment.fail()
    deployment_repository.save(deployment)

    return deployment


def test_retry_failed_deployment_resets_status(session):
    deployment = create_deployment(session)
    repository = SqlAlchemyDeploymentRepository(session)
    use_case = RetryFailedDeployment(repository)

    result = use_case.execute(deployment_id=deployment.id)

    assert result.status == DeploymentStatus.PENDING

    stored = repository.get_by_id(deployment.id)
    assert stored is not None
    assert stored.status == DeploymentStatus.PENDING


def test_retry_failed_deployment_raises_when_missing(session):
    use_case = RetryFailedDeployment(SqlAlchemyDeploymentRepository(session))

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id=uuid.uuid4())