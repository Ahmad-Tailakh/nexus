
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from nexus.infrastructure.database.models import UserModel


def test_user_can_be_persisted_and_retrieved(session):
    user = UserModel(
        email="persist-user@example.com",
        password_hash="test-password-hash",
    )

    session.add(user)
    session.commit()

    user_id = user.id

    session.expunge_all()

    result = session.get(UserModel, user_id)

    assert result is not None
    assert result.id == user_id
    assert result.email == "persist-user@example.com"
    assert result.password_hash == "test-password-hash"
    assert isinstance(result.id, uuid.UUID)
    assert result.created_at is not None
    assert result.updated_at is not None


def test_duplicate_email_is_rejected_by_database(session):
    first_user = UserModel(
        email="duplicate@example.com",
        password_hash="hash-one",
    )
    second_user = UserModel(
        email="duplicate@example.com",
        password_hash="hash-two",
    )

    session.add(first_user)
    session.commit()

    session.add(second_user)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    users = session.execute(
        select(UserModel).where(
            UserModel.email == "duplicate@example.com"
        )
    ).scalars().all()

    assert len(users) == 1
