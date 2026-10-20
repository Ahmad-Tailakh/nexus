from nexus.infrastructure.database.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)

from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError

from nexus.domain.projects.project import Project

def test_save_and_get_by_id(session):
    repository = SqlAlchemyProjectRepository(session)

    project = Project(
        name="Nexus",
        description="Production-grade backend platform",
    )

    repository.save(project)

    result = repository.get_by_id(project.id)

    assert result is not None
    assert result.id == project.id
    assert result.name == "Nexus"
    assert result.description == "Production-grade backend platform"
    assert result.created_at == project.created_at
    assert result.updated_at == project.updated_at


def test_exists_by_name_returns_true_for_existing_project(session):
    repository = SqlAlchemyProjectRepository(session)

    project = Project(name="Nexus")

    repository.save(project)

    assert repository.exists_by_name("Nexus") is True


def test_exists_by_name_returns_false_for_unknown_name(session):
    repository = SqlAlchemyProjectRepository(session)

    assert repository.exists_by_name("Unknown") is False


def test_get_by_id_returns_none_for_unknown_id(session):
    repository = SqlAlchemyProjectRepository(session)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_list_all_returns_all_projects(session):
    repository = SqlAlchemyProjectRepository(session)

    project1 = Project(name="Nexus")
    project2 = Project(name="Atlas")

    repository.save(project1)
    repository.save(project2)

    result = repository.list_all()

    assert len(result) == 2
    assert result[0].id == project1.id
    assert result[0].name == "Nexus"
    assert result[1].id == project2.id
    assert result[1].name == "Atlas"



def test_save_duplicate_name_raises_integrity_error(session):
    repository = SqlAlchemyProjectRepository(session)

    project1 = Project(name="Nexus")
    repository.save(project1)

    project2 = Project(name="Nexus")

    with pytest.raises(IntegrityError):
        repository.save(project2)



def test_delete_removes_existing_project(session):
    repository = SqlAlchemyProjectRepository(session)

    project = Project(name="Nexus")
    repository.save(project)

    repository.delete(project.id)

    result = repository.get_by_id(project.id)

    assert result is None



def test_delete_unknown_project_does_nothing(session):
    repository = SqlAlchemyProjectRepository(session)

    repository.delete(uuid4())

    assert repository.list_all() == []


