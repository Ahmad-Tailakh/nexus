import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from nexus.infrastructure.database.base import Base
from nexus.infrastructure.database.models import UserModel


def test_user_model_has_expected_table_name():
    assert UserModel.__tablename__ == "users"



def test_user_model_generates_uuid_by_default():
    user = UserModel(
        email="ahmad@example.com",
        password_hash="argon2-hash",
    )

    # SQLAlchemy applies the column default at INSERT time.
    assert user.id is None

    generated_id = UserModel.__table__.c.id.default.arg
    assert callable(generated_id)
    assert isinstance(generated_id(None), uuid.UUID)


def test_user_model_defines_required_columns():
    columns = UserModel.__table__.columns

    assert columns["id"].primary_key
    assert not columns["email"].nullable
    assert columns["email"].unique
    assert not columns["password_hash"].nullable
    assert not columns["created_at"].nullable
    assert not columns["updated_at"].nullable


def test_user_model_accepts_timezone_aware_timestamps():
    now = datetime.now(UTC)

    user = UserModel(
        email="ahmad@example.com",
        password_hash="argon2-hash",
        created_at=now,
        updated_at=now,
    )

    assert user.created_at == now
    assert user.updated_at == now