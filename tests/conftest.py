import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "app" / ".env")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured in .env")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest
from core.database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models import SessionModel, TaskModel, UserModel  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def register_payload():
    return {
        "email": "test@test.com",
        "password": "Aa@123456",
        "confirm_password": "Aa@123456",
    }


@pytest.fixture
def user(db):

    user = UserModel(
        email="test@test.com",
        username=UserModel.generate_random_username(),
    )

    user.set_password("Aa@123456")

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


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
