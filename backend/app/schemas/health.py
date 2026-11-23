from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Schema for system health check status."""

    status: str
    database: str
    environment: str
    version: str

