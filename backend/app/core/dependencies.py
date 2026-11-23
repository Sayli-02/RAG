from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

# Swagger's Authorize button posts the email as `username` to this URL.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

__all__ = ["get_db", "get_current_user", "oauth2_scheme"]


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Load the user whose id is in the Bearer token. Reject missing or bad tokens."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise credentials_error
    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user

