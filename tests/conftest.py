from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.dependencies import get_session
from app.helpers import create_access_token, get_password_hash
from app.main import app
from app.models import Role, User


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "role": Role.USER,
    }


@pytest.fixture
def test_user(test_user_data, session: Session):
    test_user_data["password"] = get_password_hash(test_user_data["password"])
    user = User(**test_user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_admin(session: Session):
    user = User(
        username="testadmin",
        email="testadmin@example.com",
        password=get_password_hash("password123"),
        role=Role.ADMIN,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User):
    return create_access_token(
        data={"sub": test_user.username, "role": test_user.role},
        expires_delta=timedelta(minutes=10),
    )


@pytest.fixture
def admin_token(test_admin: User):
    return create_access_token(
        data={"sub": test_admin.username, "role": test_admin.role},
        expires_delta=timedelta(minutes=10),
    )


@pytest.fixture
def test_users(test_admin: User, test_user: User):
    return [test_user, test_admin]
