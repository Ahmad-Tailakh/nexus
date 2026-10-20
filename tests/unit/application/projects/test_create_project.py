from unittest.mock import Mock

import pytest

from nexus.application.ports.project_repository import ProjectRepository
from nexus.domain.projects.project import Project
from nexus.application.projects.create_project import (
    CreateProject,
    ProjectNameAlreadyExistsError,
)


def test_project_can_be_created_when_name_is_available():
    # Business rule:
    # A project can be created when no existing project uses
    # the requested name.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = False

    use_case = CreateProject(repository)

    project = use_case.execute(name="Nexus")

    assert isinstance(project, Project)
    assert project.name == "Nexus"


def test_created_project_is_saved_through_repository():
    # Business rule:
    # Successfully created projects must be persisted through
    # the application's repository contract.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = False

    use_case = CreateProject(repository)

    project = use_case.execute(name="Nexus")

    repository.save.assert_called_once_with(project)


def test_duplicate_project_name_is_rejected():
    # Business rule:
    # Project names must be unique.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = True

    use_case = CreateProject(repository)

    with pytest.raises(ProjectNameAlreadyExistsError):
        use_case.execute(name="Nexus")

    repository.save.assert_not_called()


def test_repository_receives_normalized_name_when_checking_availability():
    # Business rule:
    # Name uniqueness must be checked against the normalized project name,
    # so surrounding whitespace cannot bypass the duplicate check.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = False

    use_case = CreateProject(repository)

    use_case.execute(name="   Nexus   ")

    repository.exists_by_name.assert_called_once_with("Nexus")


def test_description_is_passed_to_created_project():
    # Business rule:
    # The description supplied by the caller belongs to the created Project.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = False

    use_case = CreateProject(repository)

    project = use_case.execute(
        name="Nexus",
        description="Nexus project platform",
    )

    assert project.description == "Nexus project platform"


def test_generated_project_identity_belongs_to_saved_object():
    # Business rule:
    # The Project created by the use case receives its own identity,
    # and that exact Project instance is the one passed to the repository.
    repository = Mock(spec=ProjectRepository)
    repository.exists_by_name.return_value = False

    use_case = CreateProject(repository)

    project = use_case.execute(name="Nexus")

    saved_project = repository.save.call_args.args[0]

    assert saved_project is project
    assert saved_project.id == project.id