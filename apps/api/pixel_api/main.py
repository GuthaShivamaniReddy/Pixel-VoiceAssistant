import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pixel_api.errors import register_error_handlers
from pixel_api.middleware import CorrelationIdMiddleware
from pixel_api.routes import build_health_router
from pixel_api.runtime import VoiceRuntime
from pixel_api.settings import Settings, get_settings
from pixel_api.voice import build_voice_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    app = FastAPI(
        title="Pixel API",
        version="0.1.0",
        docs_url=None if resolved.pixel_env == "production" else "/docs",
        redoc_url=None if resolved.pixel_env == "production" else "/redoc",
    )
    app.add_middleware(CorrelationIdMiddleware)
    origins = list(resolved.cors_origin_list())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    runtime = VoiceRuntime(resolved)
    app.include_router(build_health_router(resolved))
    app.include_router(build_voice_router(runtime))
    app.state.settings = resolved
    app.state.voice = runtime
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
