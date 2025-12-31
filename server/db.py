import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# NOTE:
# - On local dev, you may still use python-dotenv via load_dotenv() in main.py.
# - On Render, env vars are injected by the platform (no .env file exists there).
# - Most importantly: DO NOT crash at import time if DATABASE_URL is missing.
#   Let the app boot so /health works, then raise only when a DB session is requested.

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

Base = declarative_base()


def get_db():
    """
    FastAPI dependency.
    Yields a DB session and ensures it closes after request.
    """
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not set. Set it as an environment variable "
            "(e.g., in Render service settings)."
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
