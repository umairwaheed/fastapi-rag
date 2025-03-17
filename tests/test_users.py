import uuid
from fastapi import status
from fastapi.testclient import TestClient

from app.models import Role, User


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
    response = client.post(
        "/users/",
        json=test_user_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_data["username"]


def test_post_user_with_less_privilege(
    client: TestClient, test_user_data: dict, user_token: str
):
    response = client.post(
        "/users/",
        json=test_user_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post("/users/", json=test_user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me(client: TestClient, test_user: User, user_token: str):
    response = client.get(
        "/users/me/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username


def test_get_me_with_less_privilege(client: TestClient):
    response = client.get("/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user(client: TestClient, test_user: User, admin_token: str):
    response = client.get(
        f"/users/{test_user.id}/", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_get_user_with_less_privilege(
    client: TestClient, test_admin: User, user_token: str
):
    response = client.get(f"/users/{test_admin.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        f"/users/{test_admin.id}/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_put_user(client: TestClient, test_user: User, admin_token: str):
    updated_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": Role.ADMIN,
    }
    response = client.put(
        f"/users/{test_user.id}/",
        json=updated_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"
    assert data["role"] == Role.ADMIN
    assert uuid.UUID(data["id"]) == test_user.id


def test_put_user_cannot_set_role(client: TestClient, test_user: User, user_token: str):
    updated_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": Role.ADMIN,
    }
    response = client.put(
        f"/users/{test_user.id}/",
        json=updated_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"
    assert data["role"] == Role.USER


def test_put_user_with_less_privilege(
    client: TestClient, test_admin: User, user_token: str
):
    updated_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": Role.USER,
    }
    response = client.put(
        f"/users/{test_admin.id}/",
        json=updated_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.put(f"/users/{test_admin.id}/", json=updated_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_user(client: TestClient, test_user: User, admin_token: str):
    response = client.delete(
        f"/users/{test_user.id}/", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_delete_user_current_user(client: TestClient, test_user: User, user_token: str):
    response = client.delete(
        f"/users/{test_user.id}/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_delete_user_with_less_privilege(
    client: TestClient, test_admin: User, user_token: str
):
    response = client.delete(f"/users/{test_admin.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(
        f"/users/{test_admin.id}/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
