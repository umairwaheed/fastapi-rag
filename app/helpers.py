import os
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext
from sentence_transformers import SentenceTransformer
from sqlmodel import Session, select

from app.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_user_by_username(session: Session, username: str):
    return session.exec(select(User).where(User.username == username)).first()


def get_user_by_id(session: Session, user_id: uuid.UUID):
    return session.get(User, user_id)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_embedding(text: str) -> list[float]:
    return embedding_model.encode(text).tolist()


def chunk_text(text: str, chunk_size: int = 256) -> list[str]:
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size])  # noqa
        for i in range(0, len(words), chunk_size)
    ]
