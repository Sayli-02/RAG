from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class DuplicateEmailError(Exception):
    """Raised when register is called with an email that already exists."""


def register_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a user with a hashed password. Email is stored in lowercase."""
    email = email.lower()
    existing = db.scalars(select(User).where(User.email == email)).first()
    if existing is not None:
        raise DuplicateEmailError

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="user",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Return the user when email and password match. Otherwise return None."""
    email = email.lower()
    user = db.scalars(select(User).where(User.email == email)).first()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
