import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.helpers import ALGORITHM, SECRET_KEY, get_user_by_username
from app.models import Role, User, engine, async_engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/")


def get_session():
    with Session(engine) as session:
        yield session


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user
