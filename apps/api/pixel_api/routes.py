from typing import Any

import psycopg
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from pixel.security import admin_access, mock_providers_allowed, record_admin_event
from pixel.security.limits import InProcessRateLimiter, client_ip
from pixel_api.settings import Settings


def _rate_limited(retry_after: int) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(retry_after)},
        content={
            "error": {
                "code": "rate_limited",
                "message": "Too many requests. Please wait and try again.",
            }
        },
    )


def build_health_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, Any]:
        if settings.pixel_env == "production":
            return {"status": "ok", "service": "pixel-api"}
        return {
            "status": "ok",
            "service": "pixel-api",
            "env": settings.pixel_env,
            "mocks_allowed": mock_providers_allowed(settings.pixel_env),
            "providers": {
                "llm": settings.llm_provider,
                "stt": settings.stt_provider,
                "tts": settings.tts_provider,
            },
        }

    @router.get("/ready")
    def ready() -> JSONResponse:
        if not settings.database_url:
            if settings.pixel_env == "production":
                return JSONResponse(
                    status_code=503,
                    content={"status": "not_ready", "database": "missing"},
                )
            return JSONResponse(
                status_code=200,
                content={"status": "ok", "database": "not_configured"},
            )
        try:
            with psycopg.connect(settings.database_url, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
        except psycopg.Error:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "database": "unreachable"},
            )
        return JSONResponse(status_code=200, content={"status": "ok", "database": "ok"})

    @router.api_route(
        "/admin/{path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    def admin_disabled(path: str, request: Request) -> JSONResponse:
        limiter: InProcessRateLimiter | None = getattr(request.app.state, "rate_limiter", None)
        if settings.rate_limit_enabled and limiter is not None:
            ip = client_ip(
                request.client.host if request.client else None,
                forwarded=request.headers.get("x-forwarded-for"),
                trust_proxy=settings.trust_proxy,
            )
            allowed, retry_after = limiter.check(
                f"admin:{ip}",
                limit=settings.rate_limit_admin_per_minute,
            )
            if not allowed:
                return _rate_limited(retry_after)
        status, code = admin_access(
            enabled=settings.admin_enabled,
            configured_token=settings.admin_token,
            authorization_header=request.headers.get("authorization"),
        )
        correlation_id = str(getattr(request.state, "correlation_id", ""))
        target = path[:80] or "root"
        if status != 200:
            record_admin_event(
                action="admin_request",
                target=target,
                result=code,
                correlation_id=correlation_id,
                actor="unauthenticated",
            )
            message = (
                "Admin API is disabled until authentication is configured"
                if code == "admin_disabled"
                else "Admin authorization is required"
            )
            return JSONResponse(
                status_code=status,
                content={"error": {"code": code, "message": message}},
            )
        record_admin_event(
            action="admin_request",
            target=target,
            result="not_found",
            correlation_id=correlation_id,
            actor="admin",
        )
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": "Unknown admin path"}},
        )

    return router
