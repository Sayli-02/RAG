from fastapi import status


def test_health_check_success(client):
    """Test /health endpoint returns 200 OK and connected status when DB responds."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "version" in data
    assert "environment" in data


def test_health_check_degraded_when_db_down(degraded_client):
    """Test /health endpoint returns degraded status when DB is unreachable."""
    response = degraded_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"] == "disconnected"

