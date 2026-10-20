
from unittest.mock import Mock
from uuid import UUID

import pytest

from nexus.application.environments.create_environment import CreateEnvironment
from nexus.application.ports.environment_repository import EnvironmentRepository
from nexus.application.ports.project_repository import ProjectRepository
from nexus.application.projects.exceptions import ProjectNotFoundError
from nexus.domain.environments.environment import Environment
from nexus.domain.projects.project import Project


def test_environment_can_be_created_for_existing_project():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    environment = use_case.execute(
        project_id=project_id,
        name="Production",
    )

    assert isinstance(environment, Environment)
    assert environment.project_id == project_id


def test_repository_retrieves_parent_project_by_id():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    use_case.execute(project_id=project_id, name="Production")

    project_repository.get_by_id.assert_called_once_with(project_id)


def test_environment_name_is_normalized_through_domain():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    environment = use_case.execute(
        project_id=project_id,
        name="   Production   ",
    )

    assert environment.name == "Production"


def test_created_environment_is_saved_through_environment_repository():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    environment = use_case.execute(
        project_id=project_id,
        name="Production",
    )

    environment_repository.save.assert_called_once_with(environment)


def test_created_environment_is_returned():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    result = use_case.execute(
        project_id=project_id,
        name="Production",
    )

    assert result is environment_repository.save.call_args.args[0]


def test_nonexistent_project_is_rejected():
    project_id = UUID("12345678-1234-5678-1234-567812345678")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = None

    environment_repository = Mock(spec=EnvironmentRepository)

    use_case = CreateEnvironment(project_repository, environment_repository)

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(
            project_id=project_id,
            name="Production",
        )

    environment_repository.save.assert_not_called()
    environment_repository.exists_by_name.assert_not_called()


def test_environment_receives_generated_identity():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    project = Project(id=project_id, name="Nexus")

    project_repository = Mock(spec=ProjectRepository)
    project_repository.get_by_id.return_value = project

    environment_repository = Mock(spec=EnvironmentRepository)
    environment_repository.exists_by_name.return_value = False

    use_case = CreateEnvironment(project_repository, environment_repository)

    environment = use_case.execute(
        project_id=project_id,
        name="Production",
    )

    assert isinstance(environment.id, UUID)