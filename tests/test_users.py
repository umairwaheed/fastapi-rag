from fastapi import status
from fastapi.testclient import TestClient

from app.models import User


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


def test_read_users_me(client: TestClient, test_user: User):
    login_response = client.post(
        "/auth/login/", data={"username": "testuser", "password": "password123"}
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
