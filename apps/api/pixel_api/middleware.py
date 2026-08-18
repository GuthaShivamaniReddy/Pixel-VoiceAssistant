from collections.abc import Awaitable, Callable
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from pixel.observability import new_correlation_id
from pixel.security.headers import api_security_headers
from pixel.security.redact import install_redacting_filter


def _valid_correlation_id(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
        candidate = (incoming or "").strip()
        correlation_id = candidate if _valid_correlation_id(candidate) else new_correlation_id()
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, hsts: bool) -> None:
        super().__init__(app)
        self._headers = api_security_headers(hsts=hsts)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        for key, value in self._headers.items():
            response.headers.setdefault(key, value)
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, max_bytes: int) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        length = request.headers.get("content-length")
        if length:
            try:
                size = int(length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {"code": "invalid_input", "message": "Invalid request size."}
                    },
                )
            if size > self._max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "payload_too_large",
                            "message": "That request is too large.",
                        }
                    },
                )
        return await call_next(request)


def configure_security_logging() -> None:
    install_redacting_filter()
