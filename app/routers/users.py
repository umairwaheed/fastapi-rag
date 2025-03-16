import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.dependencies import get_current_admin, get_current_user, get_session
from app.helpers import get_password_hash
from app.models import Role, User

router = APIRouter()


@router.get("/")
def get_all_users(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    query = select(User)

    if user.role != Role.ADMIN:
        query = query.where(User.id == user.id)

    return session.exec(query).all()


@router.post("/")
def create_user(
    user: User,
    session: Session = Depends(get_session),
):
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me/")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}/")
def read_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}/")
def update_user(
    user_id: uuid.UUID,
    updated_user: User,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = updated_user.username
    user.email = updated_user.email
    user.password = get_password_hash(updated_user.password)
    user.role = updated_user.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}/", dependencies=[Depends(get_current_admin)])
def delete_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}
