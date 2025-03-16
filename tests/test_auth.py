import jwt
from fastapi import status
from fastapi.testclient import TestClient

from app.helpers import ALGORITHM, SECRET_KEY
from app.models import User


def test_login_for_access_token(client: TestClient, test_user: User):
    response = client.post(
        "/auth/login/", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert test_user.username == payload.get("sub")
