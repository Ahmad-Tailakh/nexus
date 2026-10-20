import uuid

import pytest

from nexus.application.deployments.create_deployment import CreateDeployment
from nexus.application.deployments.exceptions import DeploymentNotFoundError
from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
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


def create_service(session):
    project = Project(name=f"Project-{uuid.uuid4()}")
    project_repository = SqlAlchemyProjectRepository(session)
    project_repository.save(project)

    environment = Environment(project_id=project.id, name="production")
    environment_repository = SqlAlchemyEnvironmentRepository(session)
    environment_repository.save(environment)

    service = __import__(
        "nexus.domain.services.service", fromlist=["Service"]
    ).Service(environment_id=environment.id, name="API")

    service_repository = SqlAlchemyServiceRepository(session)
    service_repository.save(service)

    return service


def test_create_deployment_persists_deployment(session):
    service = create_service(session)
    service_repository = SqlAlchemyServiceRepository(session)
    deployment_repository = SqlAlchemyDeploymentRepository(session)

    use_case = CreateDeployment(service_repository, deployment_repository)
    deployment = use_case.execute(service_id=service.id)

    stored = deployment_repository.get_by_id(deployment.id)

    assert stored is not None
    assert stored.id == deployment.id
    assert stored.service_id == service.id
    assert stored.status.value == "pending"


def test_create_deployment_rejects_unknown_service(session):
    use_case = CreateDeployment(
        SqlAlchemyServiceRepository(session),
        SqlAlchemyDeploymentRepository(session),
    )

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id=uuid.uuid4())