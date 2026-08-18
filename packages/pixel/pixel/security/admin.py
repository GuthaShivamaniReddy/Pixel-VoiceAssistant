"""Admin authorization. Fail closed without a configured token."""

from __future__ import annotations

import secrets


def tokens_match(expected: str, provided: str) -> bool:
    left = expected.encode("utf-8")
    right = provided.encode("utf-8")
    if len(left) != len(right):
        secrets.compare_digest(left, left)
        return False
    return secrets.compare_digest(left, right)


def admin_access(
    *,
    enabled: bool,
    configured_token: str,
    authorization_header: str | None,
) -> tuple[int, str]:
    """Return HTTP status and error code. 200/'ok' means the request may continue."""
    token = configured_token.strip()
    if not enabled or not token:
        return 403, "admin_disabled"
    header = (authorization_header or "").strip()
    if not header:
        return 401, "unauthorized"
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return 401, "unauthorized"
    if not tokens_match(token, value.strip()):
        return 401, "unauthorized"
    return 200, "ok"
