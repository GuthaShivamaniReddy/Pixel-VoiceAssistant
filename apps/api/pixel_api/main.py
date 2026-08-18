import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pixel.security.limits import InProcessRateLimiter
from pixel_api.errors import register_error_handlers
from pixel_api.middleware import (
    CorrelationIdMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    configure_security_logging,
)
from pixel_api.routes import build_health_router
from pixel_api.runtime import VoiceRuntime
from pixel_api.settings import Settings, get_settings
from pixel_api.voice import build_voice_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_security_logging()
    app = FastAPI(
        title="Pixel API",
        version="0.1.0",
        docs_url=None if resolved.pixel_env == "production" else "/docs",
        redoc_url=None if resolved.pixel_env == "production" else "/redoc",
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, hsts=resolved.use_hsts())
    app.add_middleware(RequestSizeLimitMiddleware, max_bytes=resolved.max_request_bytes)
    origins = list(resolved.cors_origin_list())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Correlation-Id", "X-Request-Id", "Authorization"],
    )
    register_error_handlers(app)
    runtime = VoiceRuntime(resolved)
    app.include_router(build_health_router(resolved))
    app.include_router(build_voice_router(runtime))
    app.state.settings = resolved
    app.state.voice = runtime
    app.state.rate_limiter = InProcessRateLimiter()
    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "pixel_api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.pixel_env == "local",
    )


if __name__ == "__main__":
    run()
