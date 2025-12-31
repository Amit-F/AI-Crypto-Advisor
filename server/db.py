import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load server/.env only for local dev convenience.
# On Render, you should set env vars in the Render dashboard.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, future=True)
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

Base = declarative_base()


def get_db():
    """
    FastAPI dependency.
    Yields a DB session and ensures it closes after request.
    """
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Set DATABASE_URL in the environment (e.g., Render service settings). "
            "For local dev, create server/.env with DATABASE_URL=..."
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
