from pixel.security.admin import admin_access, tokens_match
from pixel.security.audit import record_admin_event, record_security_event
from pixel.security.filenames import safe_basename
from pixel.security.headers import api_security_headers
from pixel.security.kill_switch import KillSwitch, parse_disabled_tools
from pixel.security.limits import InProcessRateLimiter, client_ip
from pixel.security.redact import RedactingFilter, install_redacting_filter, redact


def admin_is_enabled(flag: bool) -> bool:
    """Admin APIs fail closed unless an explicit authenticated flag is true."""
    return bool(flag)


def mock_providers_allowed(pixel_env: str) -> bool:
    """Production must not use mock LLM/STT/TTS providers (ADR-0007)."""
    return pixel_env != "production"


__all__ = [
    "InProcessRateLimiter",
    "KillSwitch",
    "RedactingFilter",
    "admin_access",
    "admin_is_enabled",
    "api_security_headers",
    "client_ip",
    "install_redacting_filter",
    "mock_providers_allowed",
    "parse_disabled_tools",
    "record_admin_event",
    "record_security_event",
    "redact",
    "safe_basename",
    "tokens_match",
]
