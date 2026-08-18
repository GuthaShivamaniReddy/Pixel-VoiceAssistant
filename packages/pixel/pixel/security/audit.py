"""Privileged-action audit records. Never log secrets or user-supplied tokens."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

log = logging.getLogger("pixel.security")


def record_admin_event(
    *,
    action: str,
    target: str,
    result: str,
    correlation_id: str,
    actor: str = "admin",
) -> None:
    log.info(
        "admin_audit actor=%s timestamp=%s action=%s target=%s result=%s correlation_id=%s",
        actor,
        datetime.now(UTC).isoformat(),
        action,
        target[:120],
        result,
        correlation_id,
    )


def record_security_event(*, kind: str, detail: str, correlation_id: str = "") -> None:
    log.info(
        "security_event type=%s detail=%s correlation_id=%s",
        kind,
        detail[:120],
        correlation_id,
    )
