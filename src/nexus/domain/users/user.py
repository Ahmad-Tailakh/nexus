
import uuid
from datetime import UTC, datetime


class User:
    """Domain entity representing a Nexus user."""

    def __init__(
        self,
        email: str,
        password_hash: str,
        *,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        normalized_email = email.strip().lower()

        if not normalized_email:
            raise ValueError("Email must not be empty.")

        if not password_hash:
            raise ValueError("Password hash must not be empty.")

        self.id = id or uuid.uuid4()
        self.email = normalized_email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or self.created_at
