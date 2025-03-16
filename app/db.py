import os

from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)
