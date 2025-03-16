import os

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

SQLModel.metadata.create_all(engine)
