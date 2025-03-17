import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.helpers import get_user_by_id, verify_password
from app.models import Role, User
from app.oso import get_oso_role


def test_get_users(client: TestClient, test_user: User, user_token: str):
    response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == test_user.username


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


def test_post_user(
    client: TestClient, test_user_data: dict, admin_token: str, session: Session
):
    response = client.post(
        "/users/",
        json=test_user_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user_data["username"]
    user = get_user_by_id(session, uuid.UUID(data["id"]))
    assert Role.USER == get_oso_role(user)


def test_post_user_can_create_admin(
    client: TestClient, test_user_data: dict, admin_token: str, session: Session
):
    test_user_data["role"] = Role.ADMIN
    response = client.post(
        "/users/",
        json=test_user_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user_data["username"]
    user = get_user_by_id(session, uuid.UUID(data["id"]))
    assert Role.ADMIN == get_oso_role(user)


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


def test_get_user_owner(client: TestClient, test_user: User, user_token: str):
    response = client.get(
        f"/users/{test_user.id}/", headers={"Authorization": f"Bearer {user_token}"}
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
    assert verify_password("newpassword", data["password"])
    assert uuid.UUID(data["id"]) == test_user.id

    # make sure this endpoint cannot set role
    assert Role.USER == get_oso_role(test_user)


def test_put_user_owner(client: TestClient, test_user: User, user_token: str):
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
    assert verify_password("newpassword", data["password"])
    assert uuid.UUID(data["id"]) == test_user.id

    # make sure this endpoint cannot set role
    assert Role.USER == get_oso_role(test_user)


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


def test_delete_user_owner(client: TestClient, test_user: User, user_token: str):
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


def test_patch_user_role(client: TestClient, test_user: User, admin_token: str):
    updated_data = {
        "role": Role.ADMIN,
    }
    response = client.patch(
        f"/users/{test_user.id}/role/",
        json=updated_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Role.ADMIN == get_oso_role(test_user)


def test_patch_user_role_with_less_privilege(
    client: TestClient, test_user: User, user_token: str
):
    updated_data = {"role": Role.ADMIN}
    response = client.patch(
        f"/users/{test_user.id}/role/",
        json=updated_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.patch(
        f"/users/{test_user.id}/role/",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
