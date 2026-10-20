from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from .exceptions import ProjectNameRequiredError


@dataclass(kw_only=True)
class Project:
    id: UUID = field(default_factory=uuid4)
    name: str
    description: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.normalize_name(self.name)
        self.updated_at = self.created_at

    @staticmethod
    def normalize_name(name: str) -> str:
        name = name.strip()

        if not name:
            raise ProjectNameRequiredError()

        return name

    def rename(self, name: str) -> None:
        name = self.normalize_name(name)

        self.name = name

        now = datetime.now(timezone.utc)

        if now <= self.updated_at:
            now = self.updated_at + timedelta(microseconds=1)

        self.updated_at = now