from typing import Any

import psycopg
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pixel.security import admin_is_enabled, mock_providers_allowed
from pixel_api.settings import Settings


def build_health_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, Any]:
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
    def admin_disabled(path: str) -> JSONResponse:
        if not admin_is_enabled(settings.admin_enabled):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "admin_disabled",
                        "message": "Admin API is disabled until authentication is configured",
                    }
                },
            )
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Unknown admin path: {path}"}},
        )

    return router
