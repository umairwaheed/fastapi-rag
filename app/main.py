import uuid
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.dependencies import get_current_admin, get_current_user, get_session
from app.helpers import (
    create_access_token,
    get_password_hash,
    get_user_by_username,
    verify_password,
)
from app.models import User

ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


@app.post("/api/token/")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = get_user_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/users/")
def create_user(
    user: User,
    session: Session = Depends(get_session),
):
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/api/users/me/")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/users/{user_id}/")
def read_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@app.put("/api/users/{user_id}/")
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


@app.delete("/api/users/{user_id}/", dependencies=[Depends(get_current_admin)])
def delete_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}
