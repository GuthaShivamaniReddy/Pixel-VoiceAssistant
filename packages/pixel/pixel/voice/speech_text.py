"""Derive a spoken line from the same grounded assistant text.

TTS must not invent a second answer. It may omit URLs and extra on-screen detail.
"""

from __future__ import annotations

import re

_URL = re.compile(r"https?://[^\s]+", re.I)
_WWW = re.compile(r"\bwww\.[^\s]+", re.I)
_MULTI_SPACE = re.compile(r"\s+")
_SENTENCE = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$", re.S)

_CYBERFLORIDA_HOST = re.compile(r"https?://(?:www\.)?cyberflorida\.org[^\s]*", re.I)

MAX_SPOKEN_SENTENCES = 4
MAX_SPOKEN_CHARS = 700


def speech_text_for_tts(
    text: str,
    *,
    has_sources: bool = False,
    has_actions: bool = False,
) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    spoken = _CYBERFLORIDA_HOST.sub("Cyber Florida's official site", raw)
    spoken = _URL.sub("the official page", spoken)
    spoken = _WWW.sub("the official page", spoken)
    spoken = _MULTI_SPACE.sub(" ", spoken).strip()
    parts = [item.strip() for item in _SENTENCE.findall(spoken) if item.strip()]
    if not parts:
        parts = [spoken]
    content = (
        parts[: MAX_SPOKEN_SENTENCES - 1]
        if _needs_screen_note(parts, has_sources, has_actions)
        else parts[:MAX_SPOKEN_SENTENCES]
    )
    spoken = " ".join(content)
    spoken = _ensure_period(spoken)
    lower = spoken.lower()
    if has_actions and not _mentions_screen(lower):
        spoken = _ensure_period(spoken) + " I've added the official resource on screen."
    elif has_sources and not _mentions_screen(lower):
        spoken = _ensure_period(spoken) + " I've included the official source on screen."
    if len(spoken) > MAX_SPOKEN_CHARS:
        spoken = spoken[: MAX_SPOKEN_CHARS - 1].rsplit(" ", 1)[0] + "."
    return spoken


def _needs_screen_note(parts: list[str], has_sources: bool, has_actions: bool) -> bool:
    joined = " ".join(parts).lower()
    return (
        (has_sources or has_actions)
        and not _mentions_screen(joined)
        and len(parts) >= MAX_SPOKEN_SENTENCES
    )


def _mentions_screen(lowered: str) -> bool:
    return bool(
        re.search(
            r"\bon screen\b|\bbelow\b|official source|official resource|added the official", lowered
        )
    )


def _ensure_period(text: str) -> str:
    stripped = text.rstrip()
    if not stripped:
        return stripped
    if stripped[-1] in ".!?":
        return stripped
    return stripped + "."
