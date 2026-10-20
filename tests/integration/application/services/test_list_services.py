import uuid

from nexus.application.services.list_services import ListServices
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


def create_environment(session):
    project = Project(name=f"Project-{uuid.uuid4()}")
    SqlAlchemyProjectRepository(session).save(project)

    environment = Environment(project_id=project.id, name="production")
    SqlAlchemyEnvironmentRepository(session).save(environment)
    return environment


def test_list_services_returns_services_sorted_by_name(session):
    environment = create_environment(session)
    repository = SqlAlchemyServiceRepository(session)

    repository.save(Service(environment_id=environment.id, name="Worker"))
    repository.save(Service(environment_id=environment.id, name="API"))

    use_case = ListServices(repository)
    result = use_case.execute(environment_id=environment.id)

    assert [service.name for service in result] == ["API", "Worker"]


def test_list_services_returns_empty_list(session):
    environment = create_environment(session)
    use_case = ListServices(SqlAlchemyServiceRepository(session))

    result = use_case.execute(environment_id=environment.id)

    assert result == []