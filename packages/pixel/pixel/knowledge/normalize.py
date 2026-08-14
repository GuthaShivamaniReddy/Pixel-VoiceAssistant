"""Normalize extracted text without rewriting facts."""

from __future__ import annotations

import hashlib
import re
import unicodedata

_WS = re.compile(r"[ \t]+")
_LINES = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [_WS.sub(" ", line).strip() for line in value.split("\n")]
    collapsed = "\n".join(line for line in lines if line)
    return _LINES.sub("\n\n", collapsed).strip()


def content_hash(text: str) -> str:
    normalized = normalize_text(text).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def token_count(text: str) -> int:
    return max(1, len(text.split()))
