"""Strict HTTPS allowlist for navigation. Parse hosts; never substring-match."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from pixel.knowledge.registry import ALLOWED_HOSTS, get_approved_source

_UNSAFE_SCHEMES = frozenset({"javascript", "data", "file", "ftp", "http", "vbscript", "about"})


def _hostname(url: str) -> str | None:
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return None
    host = parsed.hostname
    if host is None:
        return None
    return host.lower()


def is_blocked_scheme(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return True
    scheme = (parsed.scheme or "").lower()
    return scheme in _UNSAFE_SCHEMES or scheme != "https"


def looks_like_private_host(host: str) -> bool:
    if host in {"localhost", "metadata.google.internal", "metadata.google.com"}:
        return True
    if host.endswith(".local") or host.endswith(".internal"):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return bool(
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
    )


def validate_navigation_url(url: str) -> tuple[bool, str]:
    """Return (ok, reason). Only registered Cyber Florida HTTPS canonical URLs pass."""
    raw = (url or "").strip()
    if not raw or len(raw) > 500:
        return False, "invalid_destination"
    if "\\" in raw or "\n" in raw or "\r" in raw:
        return False, "invalid_destination"
    try:
        parsed = urlparse(raw)
    except ValueError:
        return False, "invalid_destination"
    scheme = (parsed.scheme or "").lower()
    if scheme in _UNSAFE_SCHEMES:
        return False, "invalid_destination"
    if scheme != "https":
        return False, "invalid_destination"
    if parsed.username or parsed.password:
        return False, "invalid_destination"
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "invalid_destination"
    if looks_like_private_host(host):
        return False, "invalid_destination"
    if host not in ALLOWED_HOSTS:
        return False, "invalid_destination"
    source = get_approved_source(raw)
    if source is None:
        return False, "invalid_destination"
    return True, "ok"


def extract_url(text: str) -> str | None:
    for token in text.split():
        piece = token.strip(".,);'\"")
        if piece.lower().startswith("http://") or piece.lower().startswith("https://"):
            return piece
    lowered = text.lower()
    for prefix in ("https://", "http://"):
        start = lowered.find(prefix)
        if start >= 0:
            return text[start:].split()[0].strip(".,);'\"")
    return None
