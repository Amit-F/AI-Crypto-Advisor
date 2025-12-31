# server/auth_utils.py
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext

# Load server/.env only for local dev convenience.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

# --- Password hashing ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT config ---
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def _get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET is not set. "
            "Set JWT_SECRET in the environment (Render service settings). "
            "For local dev, create server/.env with JWT_SECRET=..."
        )
    return secret


def create_access_token(subject: str) -> str:
    """
    subject = user identifier (we'll use user.id as string)
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Returns subject (user id) if valid, raises if invalid.
    """
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise
