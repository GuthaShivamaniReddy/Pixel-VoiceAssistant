"""Fetch only explicitly approved Cyber Florida URLs. No open-web crawl."""

from __future__ import annotations

from urllib.parse import urlparse

import httpx

from pixel.knowledge.registry import require_approved_url
from pixel.tools.urls import looks_like_private_host


def fetch_approved_html(
    url: str, *, client: httpx.Client | None = None, timeout: float = 20
) -> str:
    source = require_approved_url(url)
    parsed = urlparse(source.canonical_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or looks_like_private_host(host):
        raise ValueError("Approved source could not be fetched")
    close = client is None
    http = client or httpx.Client(timeout=timeout, follow_redirects=False)
    try:
        response = http.get(source.canonical_url)
    except httpx.HTTPError as exc:
        raise ValueError("Approved source could not be fetched") from exc
    finally:
        if close:
            http.close()
    if response.status_code >= 400:
        raise ValueError(f"Approved source fetch failed with HTTP {response.status_code}")
    text = response.text
    if not text.strip():
        raise ValueError("Approved source returned empty content")
    return text
