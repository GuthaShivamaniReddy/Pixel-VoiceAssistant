from fastapi.testclient import TestClient

from pixel_api.main import create_app
from pixel_api.settings import Settings


def test_health_ok() -> None:
    app = create_app(Settings(pixel_env="local", database_url=None))
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "pixel-api"
    assert "x-correlation-id" in response.headers


def test_ready_without_database_in_local() -> None:
    app = create_app(Settings(pixel_env="local", database_url=None))
    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "not_configured"


def test_ready_requires_database_in_production() -> None:
    app = create_app(
        Settings(
            pixel_env="production",
            database_url=None,
            llm_provider="openai",
            stt_provider="openai",
            tts_provider="openai",
            embedding_provider="openai",
        )
    )
    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 503


def test_cors_allows_configured_origin() -> None:
    app = create_app(Settings(cors_origins="http://localhost:3000"))
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_rejects_unknown_origin() -> None:
    app = create_app(Settings(cors_origins="http://localhost:3000"))
    client = TestClient(app)
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") != "http://evil.example"


def test_admin_fail_closed() -> None:
    app = create_app(Settings(admin_enabled=False))
    client = TestClient(app)
    response = client.post("/admin/sources")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_disabled"


def test_health_does_not_leak_database_url() -> None:
    app = create_app(Settings(database_url="postgresql://pixel:super-secret@localhost:5432/pixel"))
    client = TestClient(app)
    body = client.get("/health").text
    assert "super-secret" not in body
    assert "postgresql://" not in body
