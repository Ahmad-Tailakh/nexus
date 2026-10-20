from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.create_project import (
    ProjectNameAlreadyExistsError,
)
from nexus.application.projects.rename_project import (
    ProjectNotFoundError,
    RenameProject,
)
from nexus.domain.projects.project import Project


def test_existing_project_can_be_renamed():
    # Business rule:
    # An existing Project can be renamed when the new name is available.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = False

    use_case = RenameProject(repository)

    result = use_case.execute(
        project_id=project_id,
        new_name="Nexus",
    )

    assert result.name == "Nexus"


def test_repository_retrieves_project_by_id():
    # Business rule:
    # Rename must operate on the existing Project identified by its ID.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = False

    use_case = RenameProject(repository)

    use_case.execute(
        project_id=project_id,
        new_name="Nexus",
    )

    repository.get_by_id.assert_called_once_with(project_id)


def test_new_name_is_normalized_through_domain():
    # Business rule:
    # Project names are normalized by the Project domain model.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = False

    use_case = RenameProject(repository)

    use_case.execute(
        project_id=project_id,
        new_name="   Nexus   ",
    )

    assert project.name == "Nexus"


def test_rename_updates_updated_at():
    # Business rule:
    # Renaming a Project is a modification and updates its last-modified time.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )
    original_updated_at = project.updated_at

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = False

    use_case = RenameProject(repository)

    use_case.execute(
        project_id=project_id,
        new_name="Nexus",
    )

    assert project.updated_at > original_updated_at


def test_rename_does_not_change_created_at():
    # Business rule:
    # A Project's creation timestamp must remain unchanged after a rename.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )
    original_created_at = project.created_at

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = False

    use_case = RenameProject(repository)

    use_case.execute(
        project_id=project_id,
        new_name="Nexus",
    )

    assert project.created_at == original_created_at


def test_nonexistent_project_raises_project_not_found_error():
    # Business rule:
    # A Project that does not exist cannot be renamed.
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = None

    use_case = RenameProject(repository)

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(
            project_id=project_id,
            new_name="Nexus",
        )

    repository.save.assert_not_called()


def test_renaming_to_another_projects_name_is_rejected():
    # Business rule:
    # Project names must be unique.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = True

    use_case = RenameProject(repository)

    with pytest.raises(ProjectNameAlreadyExistsError):
        use_case.execute(
            project_id=project_id,
            new_name="Nexus",
        )

    assert project.name == "Atlas"
    repository.save.assert_not_called()


def test_failed_rename_is_not_saved():
    # Business rule:
    # A failed rename must not persist a partially changed Project.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Atlas",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = True

    use_case = RenameProject(repository)

    with pytest.raises(ProjectNameAlreadyExistsError):
        use_case.execute(
            project_id=project_id,
            new_name="Nexus",
        )

    repository.save.assert_not_called()


def test_renaming_project_to_its_own_name_is_rejected():
    # Business rule:
    # Renaming a Project to its current name is not considered a valid rename.
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(
        id=project_id,
        name="Nexus",
    )

    repository = Mock(spec=ProjectRepository)
    repository.get_by_id.return_value = project
    repository.exists_by_name.return_value = True

    use_case = RenameProject(repository)

    with pytest.raises(ProjectNameAlreadyExistsError):
        use_case.execute(
            project_id=project_id,
            new_name="Nexus",
        )

    repository.save.assert_not_called()