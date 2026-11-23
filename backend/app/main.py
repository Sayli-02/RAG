import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.models  # noqa: F401  — register every model so relationship names resolve
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.assistant import router as assistant_router
from app.api.comparison import router as comparison_router
from app.api.compliance import router as compliance_router
from app.api.documents import router as documents_router
from app.api.evaluation import router as evaluation_router
from app.api.research import router as research_router
from app.core.config import settings
from app.core.dependencies import get_db
from app.schemas.health import HealthCheckResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("FinScope API starting up...")
    yield
    logger.info("FinScope API shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FinScope - AI-Powered Financial Regulatory Intelligence Platform",
    lifespan=lifespan,
)

# The browser sends the JWT in the Authorization header, so cookies are not required.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(comparison_router)
app.include_router(assistant_router)
app.include_router(research_router)
app.include_router(compliance_router)
app.include_router(analytics_router)
app.include_router(evaluation_router)


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Health check endpoint",
)
def health_check(db: Session = Depends(get_db)):
    """Check API status and database connectivity."""
    db_status = "connected"
    overall_status = "ok"

    try:
        # Ping database with a simple query
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        db_status = "disconnected"
        overall_status = "degraded"

    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
    )

