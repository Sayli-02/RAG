from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Body for POST /auth/register."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value


class UserPublic(BaseModel):
    """User fields safe to return. password_hash is intentionally absent."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str


class Token(BaseModel):
    """Login response. Swagger sends this back as a Bearer token."""

    access_token: str
    token_type: str = "bearer"
