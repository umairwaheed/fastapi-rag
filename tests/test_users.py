from datetime import timedelta

import pytest
from fastapi import status
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


def test_get_users(client: TestClient, test_users: list[User], user_token: str):
    response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == test_users[0].username


def test_admin_can_get_all_users(
    client: TestClient, test_users: list[User], admin_token: str
):
    response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert {x.username for x in test_users} == {x["username"] for x in data}


def test_create_user(client: TestClient, test_user_data: dict):
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_data["username"]


def test_login_for_access_token(client: TestClient, test_user: User):
    response = client.post(
        "/auth/token/", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_read_users_me(client: TestClient, test_user: User):
    login_response = client.post(
        "/auth/token/", data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    response = client.get("/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username


def test_read_user(client: TestClient, test_user: User):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_update_user(client: TestClient, test_user: User):
    updated_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": "user",
    }
    response = client.put(f"/users/{test_user.id}/", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updateduser"


def test_delete_user(client: TestClient, test_user: User):
    response = client.delete(f"/users/{test_user.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
