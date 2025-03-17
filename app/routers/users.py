import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.dependencies import get_current_admin, get_current_user, get_session
from app.helpers import get_password_hash
from app.models import Role, User
from app.oso import add_oso_role

router = APIRouter()


@router.get("/")
def get_users(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    query = select(User)

    if user.role != Role.ADMIN:
        query = query.where(User.id == user.id)

    return session.exec(query).all()


@router.post("/", dependencies=[Depends(get_current_admin)])
def post_user(
    user: User,
    session: Session = Depends(get_session),
):
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me/")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}/")
def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if current_user.role == Role.ADMIN or current_user.id == user_id:
        user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}/")
def put_user(
    user_id: uuid.UUID,
    updated_user: User,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if current_user.role == Role.ADMIN or current_user.id == user_id:
        user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = updated_user.username
    user.email = updated_user.email
    user.password = get_password_hash(updated_user.password)

    if current_user.role == Role.ADMIN:
        # only allow admin to change role
        user.role = updated_user.role

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}/")
def delete_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if current_user.role == Role.ADMIN or current_user.id == user_id:
        user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}


class RoleUpdateRequest(BaseModel):
    role: Role


@router.patch("/{user_id}/role/")
def patch_user_role(
    user_id: uuid.UUID,
    data: RoleUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    add_oso_role(user, data.role)
    return {"message": "User role updated"}
