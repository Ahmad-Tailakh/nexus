
from unittest.mock import create_autospec

import pytest

from nexus.application.ports.user_repository import UserRepository
from nexus.application.users.errors import EmailAlreadyRegisteredError
from nexus.application.users.register_user import RegisterUser
from nexus.application.users.password_policy import validate_password
from nexus.domain.users.user import User


def test_register_user_saves_user_with_hashed_password(monkeypatch):
    repository = create_autospec(UserRepository, instance=True)
    repository.get_by_email.return_value = None

    monkeypatch.setattr(
        "nexus.application.users.register_user.hash_password",
        lambda password: "hashed-password",
    )

    register_user = RegisterUser(repository)

    user = register_user.execute(
        email="  AHMED@example.com ",
        password="StrongPassword123!",
    )

    repository.get_by_email.assert_called_once_with("ahmed@example.com")
    repository.save.assert_called_once_with(user)

    assert isinstance(user, User)
    assert user.email == "ahmed@example.com"
    assert user.password_hash == "hashed-password"
    assert user.password_hash != "StrongPassword123!"


def test_register_user_rejects_duplicate_email():
    repository = create_autospec(UserRepository, instance=True)
    repository.get_by_email.return_value = User(
        email="ahmed@example.com",
        password_hash="existing-hash",
    )

    register_user = RegisterUser(repository)

    with pytest.raises(EmailAlreadyRegisteredError):
        register_user.execute(
            email="AHMED@example.com",
            password="StrongPassword123!",
        )

    repository.save.assert_not_called()


@pytest.mark.parametrize(
    "password",
    [
        "",
        "Short123!",
        "a" * 129,
    ],
)
def test_register_user_rejects_invalid_password(password):
    repository = create_autospec(UserRepository, instance=True)
    repository.get_by_email.return_value = None

    register_user = RegisterUser(repository)

    with pytest.raises(ValueError):
        register_user.execute(
            email="ahmed@example.com",
            password=password,
        )

    repository.get_by_email.assert_not_called()
    repository.save.assert_not_called()

def test_validate_password_accepts_valid_password():
    validate_password("StrongPassword123!")


@pytest.mark.parametrize(
    "password",
    [
        "",
        "Short123!",
        "a" * 129,
    ],
)
def test_validate_password_rejects_invalid_password(password):
    with pytest.raises(ValueError):
        validate_password(password)
