"""HTTP security header values for the Pixel API."""

from __future__ import annotations

API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


def api_security_headers(*, hsts: bool) -> dict[str, str]:
    headers = {
        "Content-Security-Policy": API_CSP,
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), geolocation=(), microphone=(), payment=()",
        "X-Permitted-Cross-Domain-Policies": "none",
        "Cache-Control": "no-store",
    }
    if hsts:
        headers["Strict-Transport-Security"] = "max-age=15552000; includeSubDomains"
    return headers
