"""Redact secrets and credential-shaped values from log text."""

from __future__ import annotations

import logging
import re

_BEARER = re.compile(r"(?i)\bBearer\s+\S+")
_SK = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")
_ASSIGNED = re.compile(
    r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|"
    r"private[_-]?key|authorization|database_url|openai_api_key)\s*[:=]\s*\S+"
)
_DB_URL = re.compile(r"(?i)\b(postgres(?:ql)?|mysql|mongodb|redis)://[^\s]+")
_PEM = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----")
_OTP = re.compile(r"(?i)\b(otp|one[- ]time(?: code)?|verification code)\b[:\s]+\d{4,8}")


def redact(text: str) -> str:
    cleaned = _PEM.sub("[REDACTED_PRIVATE_KEY]", text)
    cleaned = _DB_URL.sub("[REDACTED_URL]", cleaned)
    cleaned = _BEARER.sub("Bearer [REDACTED]", cleaned)
    cleaned = _SK.sub("[REDACTED_KEY]", cleaned)
    cleaned = _ASSIGNED.sub(lambda match: f"{match.group(1)}=[REDACTED]", cleaned)
    cleaned = _OTP.sub(lambda match: f"{match.group(1)}=[REDACTED]", cleaned)
    return cleaned


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {key: _redact_arg(value) for key, value in record.args.items()}
            else:
                record.args = tuple(_redact_arg(item) for item in record.args)
        return True


def _redact_arg(value: object) -> object:
    if isinstance(value, str):
        return redact(value)
    return value


def install_redacting_filter() -> None:
    handler_filter = RedactingFilter()
    for name in ("pixel", "pixel.api", "pixel.orchestrator", "pixel.tools", "pixel.security"):
        logger = logging.getLogger(name)
        if not any(isinstance(item, RedactingFilter) for item in logger.filters):
            logger.addFilter(handler_filter)
    root = logging.getLogger()
    if not any(isinstance(item, RedactingFilter) for item in root.filters):
        root.addFilter(handler_filter)
    for handler in root.handlers:
        if not any(isinstance(item, RedactingFilter) for item in handler.filters):
            handler.addFilter(handler_filter)
