import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from nexus.infrastructure.database.base import Base

load_dotenv()

database_url = make_url(os.environ["DATABASE_URL"])
test_database_url = database_url.set(database="nexus_test")

test_engine = create_engine(
    test_database_url,
    pool_pre_ping=True,
)


@pytest.fixture
def session():
    Base.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session

    Base.metadata.drop_all(test_engine)

