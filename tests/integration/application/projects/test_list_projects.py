from nexus.application.projects.list_projects import ListProjects
from nexus.domain.projects.project import Project
from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)


def test_list_projects_returns_empty_list_when_no_projects_exist(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = ListProjects(repository)

    result = use_case.execute()

    assert result == []


def test_list_projects_returns_all_projects(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = ListProjects(repository)

    project1 = Project(
        name="Nexus",
        description="Production-grade backend platform",
    )
    project2 = Project(
        name="Atlas",
        description="Infrastructure platform",
    )

    repository.save(project1)
    repository.save(project2)

    result = use_case.execute()

    assert len(result) == 2

    assert result[0].id == project1.id
    assert result[0].name == "Nexus"
    assert result[0].description == "Production-grade backend platform"

    assert result[1].id == project2.id
    assert result[1].name == "Atlas"
    assert result[1].description == "Infrastructure platform"


def test_list_projects_returns_projects_in_creation_order(session):
    repository = SqlAlchemyProjectRepository(session)
    use_case = ListProjects(repository)

    project1 = Project(name="Nexus")
    repository.save(project1)

    project2 = Project(name="Atlas")
    repository.save(project2)

    project3 = Project(name="Orion")
    repository.save(project3)

    result = use_case.execute()

    assert [project.id for project in result] == [
        project1.id,
        project2.id,
        project3.id,
    ]

