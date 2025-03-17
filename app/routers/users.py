import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.dependencies import get_current_user, get_session, get_async_session
from app.helpers import get_password_hash, get_user_by_email, get_user_by_username
from app.models import Role, User
from app.oso import add_oso_role, delete_oso_user, is_oso_admin

router = APIRouter()


class RoleUpdateRequest(BaseModel):
    role: Role


@router.get("/")
async def get_users(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
):
    query = select(User)

    if not is_oso_admin(user):
        query = query.where(User.id == user.id)

    result = await session.execute(query)
    r = result.scalars().all()
    print("*" * 100, r)
    return result


@router.post("/")
async def post_user(
    user: User,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not is_oso_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    if get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists",
        )

    if get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already exists",
        )

    user.password = get_password_hash(user.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    add_oso_role(user, user.role)
    return user


@router.get("/me/")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}/")
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if is_oso_admin(current_user) or current_user.id == user_id:
        user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}/")
async def put_user(
    user_id: uuid.UUID,
    updated_user: User,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if is_oso_admin(current_user) or current_user.id == user_id:
        user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    current_user = get_user_by_username(session, updated_user.username)
    if current_user and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists",
        )

    current_user = get_user_by_username(session, updated_user.username)
    if current_user and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already exists",
        )

    user.username = updated_user.username
    user.email = updated_user.email
    user.password = get_password_hash(updated_user.password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}/")
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = None
    if is_oso_admin(current_user) or current_user.id == user_id:
        user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await session.delete(user)
    await session.commit()
    delete_oso_user(user)
    return {"message": "User deleted"}


@router.patch("/{user_id}/role/")
async def patch_user_role(
    user_id: uuid.UUID,
    data: RoleUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not is_oso_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    delete_oso_user(user)
    add_oso_role(user, data.role)
    return {"message": "User role updated"}
