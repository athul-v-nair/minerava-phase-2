from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert isinstance(data["version"], str)


def test_openapi_available():
    client = TestClient(app)
    resp = client.get("/docs")
    assert resp.status_code == 200
    # OpenAPI JSON
    resp2 = client.get("/openapi.json")
    assert resp2.status_code == 200
    assert resp2.json()["info"]["title"] == "Minerva API"


def test_cors_headers():
    client = TestClient(app)
    resp = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 200
    # CORS middleware should allow this origin
    assert resp.headers.get("access-control-allow-origin") in (
        "http://localhost:5173",
        "*",
    )
