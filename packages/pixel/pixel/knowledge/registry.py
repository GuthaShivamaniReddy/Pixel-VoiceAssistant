"""Explicit public Cyber Florida source allowlist. No open-web crawl."""

from __future__ import annotations

from urllib.parse import urlparse

from pixel.knowledge.models import ApprovedSource

ALLOWED_HOSTS = frozenset({"cyberflorida.org", "www.cyberflorida.org"})

PUBLIC_SOURCES: tuple[ApprovedSource, ...] = (
    ApprovedSource(
        id="cf-home",
        title="Cyber Florida",
        canonical_url="https://cyberflorida.org/",
        source_type="web_page",
        access_class="public",
        topic="overview",
        audience="public",
        fixture_key="home",
    ),
    ApprovedSource(
        id="cf-about",
        title="About Cyber Florida",
        canonical_url="https://cyberflorida.org/about/",
        source_type="web_page",
        access_class="public",
        topic="overview",
        audience="public",
        fixture_key="about",
    ),
    ApprovedSource(
        id="cf-firstline",
        title="FirstLine",
        canonical_url="https://cyberflorida.org/firstline/",
        source_type="web_page",
        access_class="public",
        topic="training",
        audience="public-sector",
        fixture_key="firstline",
    ),
    ApprovedSource(
        id="cf-cyberworks",
        title="CyberWorks",
        canonical_url="https://cyberflorida.org/cyberworks/",
        source_type="web_page",
        access_class="public",
        topic="workforce",
        audience="career-seekers",
        fixture_key="cyberworks",
    ),
    ApprovedSource(
        id="cf-cmmc",
        title="CMMC Level 1 Guide",
        canonical_url="https://cyberflorida.org/cmmc-guide/",
        source_type="web_page",
        access_class="public",
        topic="business",
        audience="business",
        fixture_key="cmmc",
    ),
    ApprovedSource(
        id="cf-cyberlaunch",
        title="CyberLaunch",
        canonical_url="https://cyberflorida.org/cyberlaunch/",
        source_type="web_page",
        access_class="public",
        topic="k12",
        audience="educators",
        fixture_key="cyberlaunch",
    ),
    ApprovedSource(
        id="cf-seccdc",
        title="SECCDC",
        canonical_url="https://cyberflorida.org/seccdc/",
        source_type="web_page",
        access_class="public",
        topic="collegiate",
        audience="students",
        fixture_key="seccdc",
    ),
    ApprovedSource(
        id="cf-events",
        title="Cyber Florida Events",
        canonical_url="https://cyberflorida.org/events/",
        source_type="web_page",
        access_class="public",
        topic="events",
        audience="public",
        fixture_key="events",
    ),
)

_BY_URL = {item.canonical_url.rstrip("/"): item for item in PUBLIC_SOURCES}
_BY_ID = {item.id: item for item in PUBLIC_SOURCES}


def is_allowlisted_source_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        return False
    return True


def get_approved_source(url: str) -> ApprovedSource | None:
    key = url.strip().split("?")[0].rstrip("/")
    if key in _BY_URL:
        return _BY_URL[key]
    if f"{key}/" in {item.canonical_url.rstrip("/") for item in PUBLIC_SOURCES}:
        return _BY_URL.get(key)
    for source in PUBLIC_SOURCES:
        if source.canonical_url.rstrip("/") == key:
            return source
    return None


def get_source_by_id(source_id: str) -> ApprovedSource | None:
    return _BY_ID.get(source_id)


def require_approved_url(url: str) -> ApprovedSource:
    source = get_approved_source(url)
    if source is None or not is_allowlisted_source_url(url):
        raise ValueError("Source URL is not on the approved Cyber Florida allowlist")
    return source
