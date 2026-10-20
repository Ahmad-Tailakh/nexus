import uuid

import pytest

from nexus.application.services.delete_service import DeleteService
from nexus.application.services.exceptions import ServiceNotFoundError
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


def test_delete_service_removes_service(session):
    service = create_service(session)
    repository = SqlAlchemyServiceRepository(session)
    use_case = DeleteService(repository)

    use_case.execute(service_id=service.id)

    assert repository.get_by_id(service.id) is None


def test_delete_service_raises_when_missing(session):
    use_case = DeleteService(SqlAlchemyServiceRepository(session))

    with pytest.raises(ServiceNotFoundError):
        use_case.execute(service_id=uuid.uuid4())