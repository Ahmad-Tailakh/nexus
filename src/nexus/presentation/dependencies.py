from collections.abc import Generator
from sqlalchemy.orm import Session
from nexus.infrastructure.database.session import SessionFactory


def get_db_session() -> Generator[Session, None, None]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()