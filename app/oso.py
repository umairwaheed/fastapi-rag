import os

from fastapi import HTTPException, status
from oso_cloud import Oso, Value

from app.models import Role, User

api_key = os.getenv("OSO_API_KEY")
oso = Oso(url="https://cloud.osohq.com", api_key=api_key)


def authorize(user: User, action: str, resource: str):
    """Check if the user is allowed to perform an action on a resource."""
    if not oso.authorize(user.id, action, resource):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def add_role(user: User, role: Role):
    oso.insert(("has_role", Value("User", user.id), role, Value("Organization", "acme")))
