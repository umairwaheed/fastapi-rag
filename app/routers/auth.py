from datetime import timedelta
from app.oso import add_role

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from app.dependencies import get_session
from app.helpers import (
    create_access_token,
    get_password_hash,
    get_user_by_username,
    verify_password,
)
from app.models import Role, User

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str


class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/login/")
def post_login(
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


@router.post("/register/")
def post_register(
    new_user: RegisterUserRequest,
    session: Session = Depends(get_session),
):
    user = User(
        username=new_user.username,
        email=new_user.email,
        password=get_password_hash(new_user.password),
        role=Role.USER,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    add_role(user, Role.USER)
    return user
