from fastapi import FastAPI

from app.routers import auth, users

app = FastAPI()

app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
