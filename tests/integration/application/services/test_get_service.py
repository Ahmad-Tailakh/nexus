
import uuid

import pytest

from nexus.application.services.exceptions import ServiceNotFoundError
from nexus.application.services.get_service import GetService
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project
from nexus.domain.services.service import Service
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
    SqlAlchemyProjectRepository(session).save(project)

    environment = Environment(project_id=project.id, name="production")
    SqlAlchemyEnvironmentRepository(session).save(environment)

    service = Service(environment_id=environment.id, name="API")
    SqlAlchemyServiceRepository(session).save(service)

    return service


def test_get_service_returns_persisted_service(session):
    service = create_service(session)
    use_case = GetService(SqlAlchemyServiceRepository(session))

    result = use_case.execute(service_id=service.id)

    assert result.id == service.id
    assert result.environment_id == service.environment_id
    assert result.name == "API"


def test_get_service_raises_when_missing(session):
    use_case = GetService(SqlAlchemyServiceRepository(session))

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id=uuid.uuid4())