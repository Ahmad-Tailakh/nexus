import uuid

import pytest

from nexus.application.deployments.create_deployment import CreateDeployment
from nexus.application.deployments.get_deployment import GetDeployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError
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

    deployment_repository = SqlAlchemyDeploymentRepository(session)
    return CreateDeployment(
        SqlAlchemyServiceRepository(session),
        deployment_repository,
    ).execute(service_id=service.id)


def test_get_deployment_returns_deployment(session):
    deployment = create_deployment(session)
    use_case = GetDeployment(SqlAlchemyDeploymentRepository(session))

    result = use_case.execute(deployment_id=deployment.id)

    assert result.id == deployment.id
    assert result.service_id == deployment.service_id


def test_get_deployment_raises_when_missing(session):
    use_case = GetDeployment(SqlAlchemyDeploymentRepository(session))

    with pytest.raises(DeploymentNotFoundError):
        use_case.execute(deployment_id=uuid.uuid4())