
def validate_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")

    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters.")
