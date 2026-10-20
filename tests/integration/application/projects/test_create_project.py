
from nexus.application.projects.exceptions import ProjectNameAlreadyExistsError
from nexus.application.projects.create_project import CreateProject
from nexus.domain.projects.exceptions import ProjectNameRequiredError
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)

import pytest


def test_create_project_creates_project(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = CreateProject(repository)

    project = use_case.execute(
        name="Nexus",
        description="Production-grade backend platform",
    )

    assert project.name == "Nexus"
    assert project.description == "Production-grade backend platform"

    stored_project = repository.get_by_id(project.id)

    assert stored_project is not None
    assert stored_project.id == project.id
    assert stored_project.name == "Nexus"
    assert stored_project.description == "Production-grade backend platform"


def test_create_project_normalizes_name(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = CreateProject(repository)

    project = use_case.execute(
        name="  Nexus  ",
    )

    assert project.name == "Nexus"

    stored_project = repository.get_by_id(project.id)

    assert stored_project is not None
    assert stored_project.name == "Nexus"


def test_create_project_rejects_duplicate_name(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = CreateProject(repository)

    use_case.execute(name="Nexus")

    try:
        use_case.execute(name="Nexus")
    except ProjectNameAlreadyExistsError:
        pass
    else:
        raise AssertionError(
            "Expected ProjectNameAlreadyExistsError"
        )


def test_create_project_rejects_empty_name(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = CreateProject(repository)

    with pytest.raises(ProjectNameRequiredError):
        use_case.execute(name="   ")

