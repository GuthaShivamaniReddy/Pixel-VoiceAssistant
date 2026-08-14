"""Output checks before a model reply reaches the client."""

from __future__ import annotations

import re

from pixel.orchestrator.fallbacks import EMPTY_REPLY, INJECTION_REFUSAL

_SECRETISH = re.compile(
    r"\b(sk-[A-Za-z0-9]{8,}|OPENAI_API_KEY|BEGIN (RSA |OPENSSH )?PRIVATE KEY)\b"
)
_POLICY_LEAK = re.compile(
    r"(you are pixel, cyber florida's ai|developer policy|system prompt:)",
    re.I,
)


class OutputInvalid(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def normalize_user_text(text: str, *, max_chars: int) -> str:
    cleaned = " ".join(text.split()).strip()
    if len(cleaned) > max_chars:
        raise OutputInvalid("That question is too long. Shorten it and try again.")
    return cleaned


def validate_assistant_text(text: str, *, max_chars: int) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise OutputInvalid(EMPTY_REPLY)
    if _SECRETISH.search(cleaned):
        raise OutputInvalid(INJECTION_REFUSAL)
    if _POLICY_LEAK.search(cleaned) and "I am Pixel" not in cleaned[:80]:
        raise OutputInvalid(INJECTION_REFUSAL)
    if len(cleaned) > max_chars:
        trimmed = cleaned[:max_chars].rsplit(" ", 1)[0].strip()
        return trimmed or cleaned[:max_chars]
    return cleaned
