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
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)
):
    user = get_user_by_username(db, form_data.username)
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
    db: Session = Depends(get_session),
):
    user.password = get_password_hash(user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/users/me/")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/users/{user_id}/")
def read_user(user_id: uuid.UUID, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@app.put("/api/users/{user_id}/")
def update_user(
    user_id: uuid.UUID,
    updated_user: User,
    db: Session = Depends(get_session),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = updated_user.username
    user.email = updated_user.email
    user.password = get_password_hash(updated_user.password)
    user.role = updated_user.role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}/", dependencies=[Depends(get_current_admin)])
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
