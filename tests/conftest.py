
import os
from collections.abc import Generator
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from nexus.domain.users.user import User
from nexus.infrastructure.database.base import Base
from nexus.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from nexus.infrastructure.security.jwt_tokens import create_access_token
from nexus.infrastructure.security.passwords import hash_password
from nexus.presentation.app import app
from nexus.presentation.dependencies.db import get_db_session

load_dotenv()

database_url = make_url(os.environ["DATABASE_URL"])
test_database_url = database_url.set(database="nexus_test")

test_engine = create_engine(
    test_database_url,
    pool_pre_ping=True,
)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    Base.metadata.create_all(test_engine)

    with Session(test_engine) as db_session:
        yield db_session

    Base.metadata.drop_all(test_engine)


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    user = User(
        id=uuid4(),
        email="integration-test@example.com",
        password_hash=hash_password("IntegrationTestPassword123!"),
    )
    SqlAlchemyUserRepository(session).save(user)
    token = create_access_token(user.id)

    saved_user = SqlAlchemyUserRepository(session).get_by_id(user.id)
    print("Test user saved:", saved_user is not None)
    print(
        "Test user ID matches:",
        saved_user is not None and saved_user.id == user.id,
    )

    with TestClient(app) as test_client:
        test_client.headers.update(
            {"Authorization": f"Bearer {token}"}
        )

        print("FIXTURE HEADER:", test_client.headers.get("Authorization"))
        print("FIXTURE TOKEN CREATED:", bool(token))

        yield test_client

    app.dependency_overrides.clear()
