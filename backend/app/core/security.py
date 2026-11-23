from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Return a bcrypt hash. The plain password is never stored."""
    # bcrypt refuses passwords longer than 72 bytes. The register schema rejects those first.
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True when plain_password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    """Sign a JWT whose subject is the user id. Expiry comes from settings."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Return the user id from a valid token. Raise ValueError if it is bad or expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid access token") from exc
