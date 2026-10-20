from unittest.mock import Mock

from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.list_projects import ListProjects
from nexus.domain.projects.project import Project


def test_projects_can_be_listed():
    # Business rule:
    # Existing Projects can be retrieved as a collection.
    project1 = Project(name="Nexus")
    project2 = Project(name="Atlas")

    repository = Mock(spec=ProjectRepository)
    repository.list_all.return_value = [project1, project2]

    use_case = ListProjects(repository)

    result = use_case.execute()

    assert result[0] is project1
    assert result[1] is project2


def test_repository_lists_all_projects():
    # Business rule:
    # Listing Projects delegates retrieval to the repository.
    repository = Mock(spec=ProjectRepository)
    repository.list_all.return_value = []

    use_case = ListProjects(repository)

    use_case.execute()

    repository.list_all.assert_called_once_with()


def test_empty_project_list_is_valid():
    # Business rule:
    # The system can have zero Projects; an empty collection is a valid result.
    repository = Mock(spec=ProjectRepository)
    repository.list_all.return_value = []

    use_case = ListProjects(repository)

    result = use_case.execute()

    assert result == []