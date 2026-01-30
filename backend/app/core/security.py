"""
Security utilities - authentication, hashing, tokens.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_anonymous_id() -> str:
    """Generate a unique anonymous ID for users."""
    return secrets.token_urlsafe(16)


def hash_user_id(user_id: str) -> str:
    """Hash a user ID for analytics (privacy-preserving)."""
    return hashlib.sha256(
        f"{user_id}{settings.SECRET_KEY}".encode()
    ).hexdigest()[:16]
