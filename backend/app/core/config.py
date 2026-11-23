from pathlib import Path
from typing import Optional
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env, so the secret loads whether the process starts in backend/ or the repo root.
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "FinScope"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "finscope"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Embedding and vector configuration
    VECTOR_DIMENSION: int = 384
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    MAX_UPLOAD_BYTES: int = 20 * 1024 * 1024
    UPLOAD_DIR: str = str(Path(__file__).resolve().parents[2] / "uploads")

    # JWT. JWT_SECRET_KEY has no default so a missing secret fails at startup.
    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 60

    # Comma-separated browser origins allowed to call this API.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Retrieval and generation. An empty Gemini key is allowed so the API can boot in tests.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RETRIEVAL_K: int = 10
    RERANK_K: int = 4

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        """Browser origins allowed to call the API. Blank entries are dropped."""
        return split_origins(self.CORS_ORIGINS)

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct database connection URL if not explicitly supplied."""
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


def split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
