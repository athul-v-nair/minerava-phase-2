import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import (
    JWT_ACCESS_TTL_SECONDS,
    JWT_ALGORITHM,
    JWT_REFRESH_TTL_SECONDS,
    JWT_SECRET,
)


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _now() -> datetime:
    return datetime.now(UTC)


def create_access_token(*, user_id: str, email: str, org_id: str | None, role: str) -> str:
    now = _now()
    payload = {
        "sub": user_id,
        "email": email,
        "org_id": org_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=JWT_ACCESS_TTL_SECONDS)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(*, user_id: str) -> tuple[str, str, datetime]:
    jti = str(uuid.uuid4())
    now = _now()
    exp = now + timedelta(seconds=JWT_REFRESH_TTL_SECONDS)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, jti, exp


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
