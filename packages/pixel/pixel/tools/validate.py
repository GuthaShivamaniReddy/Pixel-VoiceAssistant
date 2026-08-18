"""Validate tool arguments. Do not trust model JSON shape alone."""

from __future__ import annotations

from collections.abc import Mapping

MAX_STRING = 400
MAX_FIELDS = 8


def validate_arguments(
    arguments: Mapping[str, object],
    *,
    allowed: Mapping[str, str],
    required: tuple[str, ...],
) -> dict[str, str]:
    if len(arguments) > MAX_FIELDS:
        raise ValueError("invalid_input")
    cleaned: dict[str, str] = {}
    for key, value in arguments.items():
        if key not in allowed:
            raise ValueError("invalid_input")
        expected = allowed[key]
        if not isinstance(value, str):
            raise ValueError("invalid_input")
        text = value.strip()
        if len(text) > MAX_STRING:
            raise ValueError("invalid_input")
        if expected == "enum_audience":
            allowed_values = {
                "",
                "public",
                "students",
                "educators",
                "business",
                "public-sector",
                "career-seekers",
            }
            if text.lower() not in allowed_values:
                raise ValueError("invalid_input")
            text = text.lower()
        cleaned[key] = text
    for field in required:
        if not cleaned.get(field):
            raise ValueError("invalid_input")
    return cleaned
