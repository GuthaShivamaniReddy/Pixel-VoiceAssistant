from fastapi.testclient import TestClient

from pixel_api.main import create_app
from pixel_api.settings import Settings


def _client(**overrides: object) -> TestClient:
    values: dict[str, object] = {
        "pixel_env": "local",
        "database_url": None,
        "cors_origins": "http://testserver",
        "llm_max_attempts": 1,
        "llm_retry_backoff_seconds": 0,
    }
    values.update(overrides)
    return TestClient(create_app(Settings(**values)))  # type: ignore[arg-type]


def test_admin_disabled_without_token() -> None:
    client = _client(admin_enabled=True, admin_token="")
    response = client.post("/admin/sources")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_disabled"


def test_admin_requires_bearer_token() -> None:
    client = _client(admin_enabled=True, admin_token="local-admin-token-for-tests")
    missing = client.post("/admin/reindex")
    assert missing.status_code == 401
    wrong = client.post("/admin/ingestion/job-1", headers={"Authorization": "Bearer nope"})
    assert wrong.status_code == 401
    ok = client.get(
        "/admin/sources",
        headers={"Authorization": "Bearer local-admin-token-for-tests"},
    )
    assert ok.status_code == 404
    assert ok.json()["error"]["code"] == "not_found"


def test_client_supplied_admin_header_does_not_open_admin() -> None:
    client = _client(admin_enabled=False)
    response = client.post("/admin/sources", json={"isAdmin": True}, headers={"X-Admin": "true"})
    assert response.status_code == 403


def test_idor_unknown_session_is_not_found() -> None:
    client = _client()
    created = client.post("/v1/sessions").json()["session_id"]
    other = "00000000-0000-4000-8000-000000000000"
    assert created != other
    response = client.post(
        "/v1/turns",
        json={
            "session_id": other,
            "turn_id": "x",
            "text": "What is Cyber Florida?",
            "speak": False,
        },
    )
    assert response.status_code == 404


def test_security_headers_present() -> None:
    client = _client()
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "strict-transport-security" not in {key.lower() for key in response.headers}


def test_hsts_in_production() -> None:
    client = _client(
        pixel_env="production",
        llm_provider="openai",
        stt_provider="openai",
        tts_provider="openai",
        embedding_provider="openai",
        hsts_enabled=True,
    )
    response = client.get("/health")
    assert "max-age=" in response.headers.get("strict-transport-security", "")
    body = response.json()
    assert "env" not in body
    assert "providers" not in body


def test_rate_limit_sessions_returns_429() -> None:
    client = _client(rate_limit_session_per_minute=2)
    assert client.post("/v1/sessions").status_code == 201
    assert client.post("/v1/sessions").status_code == 201
    limited = client.post("/v1/sessions")
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "rate_limited"
    assert limited.headers.get("retry-after")


def test_oversized_json_rejected() -> None:
    client = _client(max_request_bytes=128)
    response = client.post(
        "/v1/turns",
        json={"turn_id": "huge", "text": "x" * 400, "speak": False},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_untrusted_correlation_id_is_replaced() -> None:
    client = _client()
    response = client.get("/health", headers={"X-Correlation-Id": "not a uuid\nInjection"})
    assert response.headers["x-correlation-id"] != "not a uuid\nInjection"
    assert "Injection" not in response.headers["x-correlation-id"]


def test_cors_still_rejects_unknown_origin() -> None:
    client = _client(cors_origins="http://localhost:3000")
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert response.headers.get("access-control-allow-origin") != "http://evil.example"
