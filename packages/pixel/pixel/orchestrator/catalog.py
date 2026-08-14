"""Allowlisted public pointers used until Phase 6 retrieval exists."""

from pixel.domain import RecommendedAction, SourceRef

ABOUT = SourceRef(
    title="About Cyber Florida",
    name="Cyber Florida",
    url="https://cyberflorida.org/about/",
    description="Public overview of the Florida Center for Cybersecurity at USF.",
    provenance="policy",
)

HOME = SourceRef(
    title="Cyber Florida",
    name="Cyber Florida",
    url="https://cyberflorida.org/",
    description="Public Cyber Florida homepage. Not live retrieval.",
    provenance="policy",
)

OPEN_HOME = RecommendedAction(
    id="view-site",
    label="Open Cyber Florida",
    href="https://cyberflorida.org/",
)

OPEN_ABOUT = RecommendedAction(
    id="view-about",
    label="Open resource",
    href="https://cyberflorida.org/about/",
)

ALLOWED_HOSTS = frozenset({"cyberflorida.org", "www.cyberflorida.org"})


def is_allowlisted_url(url: str) -> bool:
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme != "https":
            return False
        return parsed.hostname is not None and parsed.hostname.lower() in ALLOWED_HOSTS
    except ValueError:
        return False


def filter_sources(sources: list[SourceRef]) -> list[SourceRef]:
    return [source for source in sources if is_allowlisted_url(source.url)]


def filter_actions(actions: list[RecommendedAction]) -> list[RecommendedAction]:
    return [action for action in actions if is_allowlisted_url(action.href)]
