import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext

load_dotenv()

# --- Password hashing ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT config ---
JWT_SECRET = os.getenv("JWT_SECRET")

# In production we MUST have a secret. Locally it's fine to fall back.
ENV = os.getenv("ENV", "development").lower()

if not JWT_SECRET:
    if ENV in ("production", "prod"):
        raise RuntimeError("JWT_SECRET is not set")
    # Dev fallback so local runs don't crash.
    JWT_SECRET = "dev-insecure-secret-change-me"

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h default


def create_access_token(subject: str) -> str:
    """
    subject = user identifier (we'll use user.id as string)
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        # Use numeric timestamp to be unambiguous everywhere
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Returns subject (user id) if valid, raises JWTError if invalid.
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    sub = payload.get("sub")
    if not sub:
        raise JWTError("Missing sub")
    return sub
