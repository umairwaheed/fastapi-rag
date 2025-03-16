from fastapi import status
from fastapi.testclient import TestClient

from app.models import User


def test_get_users(client: TestClient, test_users: list[User], user_token: str):
    response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == test_users[0].username


def test_get_users_with_admin_role(
    client: TestClient, test_users: list[User], admin_token: str
):
    response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert {x.username for x in test_users} == {x["username"] for x in data}


def test_get_users_with_less_privilege(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_post_user(client: TestClient, test_user_data: dict, admin_token: str):
    response = client.post("/users/", json=test_user_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_data["username"]


def test_post_user_with_less_privilege(client: TestClient, test_user_data: dict, user_token: str):
    response = client.post("/users/", json=test_user_data, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post("/users/", json=test_user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me(client: TestClient, test_user: User, user_token: str):
    response = client.get("/users/me/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username


def test_get_me_with_less_privilege(client: TestClient):
    response = client.get("/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user(client: TestClient, test_user: User):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_put_user(client: TestClient, test_user: User):
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
