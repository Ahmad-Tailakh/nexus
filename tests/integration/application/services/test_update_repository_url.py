import uuid

from nexus.application.services.update_repository_url import UpdateRepositoryUrl
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


def test_update_repository_url_persists_change(session):
    service = create_service(session)
    repository = SqlAlchemyServiceRepository(session)
    use_case = UpdateRepositoryUrl(repository)

    result = use_case.execute(
        service_id=service.id,
        repository_url="https://github.com/example/api",
    )

    stored = repository.get_by_id(service.id)

    assert result.repository_url == "https://github.com/example/api"
    assert stored is not None
    assert stored.repository_url == "https://github.com/example/api"


def test_update_repository_url_can_clear_url(session):
    service = create_service(session)
    service.update_repository_url("https://github.com/example/api")

    repository = SqlAlchemyServiceRepository(session)
    repository.save(service)

    use_case = UpdateRepositoryUrl(repository)
    result = use_case.execute(service_id=service.id, repository_url=None)

    assert result.repository_url is None
    assert repository.get_by_id(service.id).repository_url is None