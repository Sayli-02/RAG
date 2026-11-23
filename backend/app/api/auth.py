from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import Token, UserPublic, UserRegister
from app.services.auth_service import DuplicateEmailError, authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, db: Session = Depends(get_db)):
    """Create an account. The response never includes the password hash."""
    try:
        user = register_user(db, name=body.name, email=body.email, password=body.password)
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Check email and password, then return a JWT.

    Swagger's Authorize button sends the email in the OAuth2 `username` field.
    """
    user = authenticate_user(db, email=form.username, password=form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)):
    """Return the user identified by the Bearer token."""
    return current_user
