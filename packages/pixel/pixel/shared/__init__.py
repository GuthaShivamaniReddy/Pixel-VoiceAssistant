"""Shared constants. No secrets live here."""

from pixel.shared.cancellation import CancellationFlag, CancelledError

PUBLIC_ENV_PREFIX = "NEXT_PUBLIC_"
FORBIDDEN_PUBLIC_SUBSTRINGS = ("SECRET", "API_KEY", "TOKEN", "PASSWORD", "PRIVATE")

PIXEL_ENVIRONMENTS = ("local", "development", "staging", "production")

__all__ = [
    "PUBLIC_ENV_PREFIX",
    "FORBIDDEN_PUBLIC_SUBSTRINGS",
    "PIXEL_ENVIRONMENTS",
    "CancellationFlag",
    "CancelledError",
]
