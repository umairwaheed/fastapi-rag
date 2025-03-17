import jwt
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.helpers import ALGORITHM, SECRET_KEY, get_user_by_id
from app.models import Role, User
from app.oso import get_oso_role


def test_login_for_access_token(client: TestClient, test_user: User):
    response = client.post(
        "/auth/login/", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert test_user.username == payload.get("sub")


def test_post_register(client: TestClient, test_user_data: dict, session: Session):
    response = client.post("/auth/register/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["username"] == test_user_data["username"]

    user = get_user_by_id(session, data["id"])
    assert Role.USER == get_oso_role(user)


def test_post_register_cannot_set_admin_role(
    client: TestClient, test_user_data: dict, session: Session
):
    test_user_data["role"] = Role.ADMIN
    response = client.post("/auth/register/", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["role"] == Role.USER

    user = get_user_by_id(session, data["id"])
    assert Role.USER == get_oso_role(user)
