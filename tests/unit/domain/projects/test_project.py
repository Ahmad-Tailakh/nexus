from datetime import timezone
from uuid import UUID

import pytest

from nexus.domain.projects.exceptions import ProjectNameRequiredError
from nexus.domain.projects.project import Project


def test_project_can_be_created_with_valid_name():
    # Business rule:
    # A Project can be created when it has a meaningful name.
    project = Project(name="Nexus")

    assert project.name == "Nexus"


def test_project_strips_surrounding_whitespace_from_name():
    # Business rule:
    # A Project name should be stored in a normalized form.
    project = Project(name="   Nexus   ")

    assert project.name == "Nexus"


def test_project_rejects_empty_name():
    # Business rule:
    # A Project must have a meaningful name.
    with pytest.raises(ProjectNameRequiredError):
        Project(name="")


def test_project_rejects_whitespace_only_name():
    # Business rule:
    # Whitespace is not a meaningful Project name.
    with pytest.raises(ProjectNameRequiredError):
        Project(name="   ")


def test_project_description_defaults_to_none():
    # Business rule:
    # A Project may exist without a description.
    project = Project(name="Nexus")

    assert project.description is None


def test_project_generates_uuid_automatically():
    # Business rule:
    # Every Project must have a unique identity without requiring
    # the caller to provide one.
    project = Project(name="Nexus")

    assert isinstance(project.id, UUID)


def test_two_projects_get_different_uuids():
    # Business rule:
    # Separate Project instances must have distinct identities.
    project1 = Project(name="Nexus")
    project2 = Project(name="Atlas")

    assert project1.id != project2.id


def test_project_created_at_is_timezone_aware_utc():
    # Business rule:
    # Project creation timestamps must unambiguously represent UTC time.
    project = Project(name="Nexus")

    assert project.created_at.tzinfo is not None
    assert project.created_at.utcoffset() == timezone.utc.utcoffset(
        project.created_at
    )


def test_project_updated_at_is_timezone_aware_utc():
    # Business rule:
    # Project update timestamps must unambiguously represent UTC time.
    project = Project(name="Nexus")

    assert project.updated_at.tzinfo is not None
    assert project.updated_at.utcoffset() == timezone.utc.utcoffset(
        project.updated_at
    )


def test_two_projects_receive_independently_generated_timestamps():
    # Business rule:
    # Timestamps belong to individual Project instances and must not
    # accidentally be shared through a class-level/default value.
    project1 = Project(name="Nexus")
    project2 = Project(name="Atlas")

    assert project1.created_at is not project2.created_at
    assert project1.updated_at is not project2.updated_at


def test_new_project_created_at_equals_updated_at():
    # Business rule:
    # A newly created Project has not been updated yet, so its
    # creation and update timestamps represent the same moment.
    project = Project(name="Nexus")

    assert project.created_at == project.updated_at


def test_rename_updates_project_name():
    # Business rule:
    # Renaming a Project changes its name.
    project = Project(name="Nexus")

    project.rename("Nexus Platform")

    assert project.name == "Nexus Platform"


def test_rename_strips_surrounding_whitespace():
    # Business rule:
    # Project names are stored in normalized form.
    project = Project(name="Nexus")

    project.rename("   Nexus Platform   ")

    assert project.name == "Nexus Platform"


def test_rename_rejects_empty_name():
    # Business rule:
    # A Project must always have a meaningful name.
    project = Project(name="Nexus")

    with pytest.raises(ProjectNameRequiredError):
        project.rename("")


def test_rename_rejects_whitespace_only_name():
    # Business rule:
    # Whitespace is not a meaningful Project name.
    project = Project(name="Nexus")

    with pytest.raises(ProjectNameRequiredError):
        project.rename("   ")


def test_rename_updates_updated_at():
    # Business rule:
    # Renaming a Project is a modification and must update its
    # last-modified timestamp.
    project = Project(name="Nexus")
    original_updated_at = project.updated_at

    project.rename("Nexus Platform")

    assert project.updated_at >= original_updated_at


def test_rename_does_not_change_created_at():
    # Business rule:
    # A Project's creation timestamp represents when it was originally
    # created and must remain unchanged through a rename.
    project = Project(name="Nexus")
    original_created_at = project.created_at

    project.rename("Nexus Platform")

    assert project.created_at == original_created_at


def test_rename_returns_none():
    # Business rule:
    # rename() mutates the existing Project rather than creating
    # or returning another Project.
    project = Project(name="Nexus")

    result = project.rename("Nexus Platform")

    assert result is None


def test_failed_rename_does_not_modify_project():
    # Business rule:
    # A failed rename must leave the Project unchanged.
    project = Project(name="Nexus")

    original_name = project.name
    original_updated_at = project.updated_at

    with pytest.raises(ProjectNameRequiredError):
        project.rename("   ")

    assert project.name == original_name
    assert project.updated_at == original_updated_at
