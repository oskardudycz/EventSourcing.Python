import os
import pytest
from typing import Generator, cast
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer  # type: ignore

from appending_events_db.src.appending_events_db.event_store import EventStore
from appending_events_db.src.appending_events_db.model import Base

postgres = PostgresContainer("postgres:17-alpine")


@pytest.fixture(scope="session", autouse=True)
def setup(request: pytest.FixtureRequest) -> str:
    postgres.start()

    def remove_container() -> None:
        postgres.stop()

    request.addfinalizer(remove_container)
    os.environ["DB_CONN"] = postgres.get_connection_url()
    os.environ["DB_HOST"] = postgres.get_container_host_ip()
    os.environ["DB_PORT"] = postgres.get_exposed_port(5432)
    os.environ["DB_USERNAME"] = postgres.username
    os.environ["DB_PASSWORD"] = postgres.password
    os.environ["DB_NAME"] = postgres.dbname
    return cast(str, postgres.get_connection_url())


@pytest.fixture(scope="session")
def db_session(setup: str) -> Generator[Session, None, None]:
    engine = create_engine(setup)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def event_store(db_session: Session) -> EventStore:
    return EventStore(db_session)
