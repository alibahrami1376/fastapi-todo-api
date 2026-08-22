import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "app" / ".env")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured in .env")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
# Avoid Redis/rate-limit coupling in the unit/integration suite
os.environ["RATE_LIMIT_ENABLED"] = "false"

from core.database import Base, get_db
from main import app
from models import SessionModel, TaskModel, UserModel  # noqa: F401

# ---------------------------------------------------------
# Test Database
# ---------------------------------------------------------

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    session.begin_nested()

    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    event.listen(session, "after_transaction_end", restart_savepoint)

    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", restart_savepoint)
        session.close()
        transaction.rollback()
        connection.close()


# ---------------------------------------------------------
# Client
# ---------------------------------------------------------


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# Auth Payloads
# ---------------------------------------------------------


@pytest.fixture
def register_payload():
    return {
        "email": "test@test.com",
        "password": "Aa@123456",
        "confirm_password": "Aa@123456",
    }


@pytest.fixture
def login_payload():
    return {
        "email": "test@test.com",
        "password": "Aa@123456",
    }


@pytest.fixture
def invalid_login_payload():
    return {
        "email": "test@test.com",
        "password": "Bb@123456",
    }


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------


@pytest.fixture
def user(db):
    user = UserModel(
        email="test@test.com",
        username=UserModel.generate_random_username(),
    )
    user.set_password("Aa@123456")
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


@pytest.fixture
def second_user(db):
    user = UserModel(
        email="second@test.com",
        username=UserModel.generate_random_username(),
    )
    user.set_password("Bb@123456")
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


# ---------------------------------------------------------
# Authenticated Clients
# ---------------------------------------------------------


def _login_client(client, email, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.json()
    client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
    return client


@pytest.fixture
def authenticated_client(client, user):
    return _login_client(client, user.email, "Aa@123456")


@pytest.fixture
def login_tokens(client, user):
    """Return the raw login response dict (access_token + refresh_token)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Aa@123456"},
    )
    assert response.status_code == 200, response.json()
    return response.json()


@pytest.fixture
def second_authenticated_client(client, second_user):
    second_client = TestClient(app)
    return _login_client(second_client, second_user.email, "Bb@123456")


# ---------------------------------------------------------
# Task
# ---------------------------------------------------------


@pytest.fixture
def task_payload():
    return {
        "title": "Test Task",
        "description": "Task description",
        "priority": "low",
        "due_date": None,
    }
