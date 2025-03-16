from fastapi import FastAPI

from app.routers import auth, rag, users

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

app.include_router(
    rag.router,
    prefix="/rag",
    tags=["rag"],
)
