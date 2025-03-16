import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from main import Role, User, app, get_password_hash, get_session


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


def test_create_user(client: TestClient, test_user_data: dict):
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_data["username"]


def test_login_for_access_token(client: TestClient, test_user: User):
    response = client.post(
        "/api/token/", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_read_users_me(client: TestClient, test_user: User):
    login_response = client.post(
        "/api/token/", data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/api/users/me/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username


def test_read_user(client: TestClient, test_user: User):
    response = client.get(f"/api/users/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_update_user(client: TestClient, test_user: User):
    updated_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": "user",
    }
    response = client.put(f"/api/users/{test_user.id}/", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updateduser"


def test_delete_user(client: TestClient, test_user: User):
    response = client.delete(f"/api/users/{test_user.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
