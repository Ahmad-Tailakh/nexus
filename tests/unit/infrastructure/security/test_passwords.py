
from nexus.infrastructure.security.passwords import (
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plaintext():
    password = "correct-horse-battery-staple"

    password_hash = hash_password(password)

    assert password_hash != password


def test_verify_password_accepts_correct_password():
    password = "correct-horse-battery-staple"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_password_rejects_incorrect_password():
    password_hash = hash_password("correct-password")

    assert verify_password("incorrect-password", password_hash) is False


def test_hash_password_uses_a_different_salt_for_each_hash():
    password = "correct-horse-battery-staple"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True
