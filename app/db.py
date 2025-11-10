from sqlmodel import SQLModel, create_engine, Session
import os

DB_URL = os.getenv("DB_URL", "sqlite:///./data.db")
engine = create_engine(DB_URL, echo=False)

def init_db():
    from .models import Audit
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
