import os

from fastapi import HTTPException, status
from oso_cloud import Oso, Value

from app.models import Role, User

api_key = os.getenv("OSO_API_KEY")
oso_url = os.getenv("OSO_URL")
oso = Oso(url=oso_url, api_key=api_key)


def authorize(user: User, action: str, resource: str):
    """Check if the user is allowed to perform an action on a resource."""
    if not oso.authorize(user.id, action, resource):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def delete_oso_user(user: User):
    oso.delete(("has_role", Value("User", user.id), None, None))


def add_oso_role(user: User, role: Role):
    oso.insert(
        ("has_role", Value("User", user.id), role, Value("Organization", "acme"))
    )


def get_oso_role(user: User):
    response = oso.get(
        ("has_role", Value("User", user.id), None, Value("Organization", "acme"))
    )
    try:
        return response[0][2].id
    except Exception:
        pass


def is_oso_admin(user: User):
    return oso.authorize(Value("User", user.id), "edit", Value("Organization", "acme"))
