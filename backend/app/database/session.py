from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine manages database connections
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)

# SessionLocal factory creates a new Session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session and guarantees cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
