import jwt
from fastapi import status
from fastapi.testclient import TestClient

from app.helpers import ALGORITHM, SECRET_KEY
from app.models import Role, User


def test_login_for_access_token(client: TestClient, test_user: User):
    response = client.post(
        "/auth/login/", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert test_user.username == payload.get("sub")


def test_post_register(client: TestClient, test_user_data: dict):
    response = client.post("/auth/register/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_data["username"]


def test_post_register_cannot_set_admin_role(client: TestClient, test_user_data: dict):
    test_user_data["role"] = Role.ADMIN
    response = client.post("/auth/register/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == Role.USER
