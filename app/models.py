import os
import uuid
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector
from psycopg2 import connect
from sqlmodel import Field, SQLModel, create_engine

USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB = os.getenv("POSTGRES_DB")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG") == "True")

connection = connect(database=DB, user=USER, password=PASSWORD, host=HOST, port=PORT)
connection.autocommit = True
with connection.cursor() as cursor:
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

connection.close()


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str
    role: Role = Field(default=Role.USER)


class Document(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str = Field()


class Chunk(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(foreign_key="document.id")
    chunk_text: str
    embedding: Any = Field(sa_type=Vector(384))


SQLModel.metadata.create_all(engine)
