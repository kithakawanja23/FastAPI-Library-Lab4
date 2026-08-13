import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

# Check for DATABASE_URL; if missing (like on Render), default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./database.db"

# SQLite requires check_same_thread=False for FastAPI
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Dependency for getting a database session"""
    with Session(engine) as session:
        yield session
