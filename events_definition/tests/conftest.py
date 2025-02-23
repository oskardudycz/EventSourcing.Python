import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer


postgres = PostgresContainer("postgres:17-alpine")

connection_url = None


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
    os.environ["DB_CONN"] = postgres.get_connection_url()
    os.environ["DB_HOST"] = postgres.get_container_host_ip()
    os.environ["DB_PORT"] = postgres.get_exposed_port(5432)
    os.environ["DB_USERNAME"] = postgres.username
    os.environ["DB_PASSWORD"] = postgres.password
    os.environ["DB_NAME"] = postgres.dbname
    global connection_url
    return postgres.get_connection_url()


@pytest.fixture(scope="session")
def db_session(setup):
    engine = create_engine(setup)
    with Session(engine) as session:
        yield session
