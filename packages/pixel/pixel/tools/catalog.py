"""Program/resource catalog from the Phase 6 source registry. No second RAG index."""

from __future__ import annotations

from pixel.knowledge.models import ApprovedSource
from pixel.knowledge.registry import PUBLIC_SOURCES

PROGRAM_IDS = frozenset({"cf-firstline", "cf-cyberworks", "cf-cmmc", "cf-cyberlaunch", "cf-seccdc"})

_AUDIENCE_ALIASES = {
    "student": "students",
    "students": "students",
    "beginner": "career-seekers",
    "beginners": "career-seekers",
    "educator": "educators",
    "educators": "educators",
    "teacher": "educators",
    "k12": "educators",
    "k-12": "educators",
    "business": "business",
    "company": "business",
    "public sector": "public-sector",
    "government": "public-sector",
    "career": "career-seekers",
}


def detect_audience(text: str) -> str:
    key = text.lower()
    for needle, audience in _AUDIENCE_ALIASES.items():
        if needle in key:
            return audience
    return ""


def detect_topic(text: str) -> str:
    key = text.lower()
    mapping = {
        "firstline": "training",
        "training": "training",
        "workforce": "workforce",
        "cyberworks": "workforce",
        "cmmc": "business",
        "cyberlaunch": "k12",
        "seccdc": "collegiate",
        "competition": "collegiate",
        "event": "events",
    }
    for needle, topic in mapping.items():
        if needle in key:
            return topic
    return ""


def _matches(source: ApprovedSource, *, audience: str, topic: str, keywords: str) -> bool:
    if not source.active:
        return False
    if audience:
        if audience == "students":
            if source.audience not in {"students", "career-seekers"}:
                return False
        elif source.audience != audience:
            return False
    if topic and source.topic != topic:
        return False
    if keywords and not audience and not topic:
        blob = f"{source.title} {source.topic} {source.audience} {source.id}".lower()
        tokens = [token for token in keywords.lower().split() if len(token) > 3]
        if tokens and not any(token in blob for token in tokens):
            return False
    return True


def list_sources(
    *,
    programs_only: bool = False,
    audience: str = "",
    topic: str = "",
    keywords: str = "",
    sources: tuple[ApprovedSource, ...] | None = None,
) -> tuple[ApprovedSource, ...]:
    inventory = sources or PUBLIC_SOURCES
    found: list[ApprovedSource] = []
    for source in inventory:
        if programs_only and source.id not in PROGRAM_IDS:
            continue
        if _matches(source, audience=audience, topic=topic, keywords=keywords):
            found.append(source)
    return tuple(found)
