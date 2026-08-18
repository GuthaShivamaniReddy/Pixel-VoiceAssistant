"""Production tool handlers. No HTTP, shell, or database query tools."""

from __future__ import annotations

from pixel.domain import Citation, RecommendedAction, SourceRef
from pixel.knowledge import Retriever, fixture_retriever
from pixel.knowledge.models import ApprovedSource
from pixel.knowledge.registry import get_source_by_id
from pixel.tools.catalog import list_sources
from pixel.tools.registry import ToolRegistry
from pixel.tools.types import NormalizedToolResult, ToolDefinition
from pixel.tools.urls import validate_navigation_url

DEFAULT_TIMEOUT = 5.0


def _source_ref(source: ApprovedSource) -> SourceRef:
    return SourceRef(
        title=source.title,
        name="Cyber Florida",
        url=source.canonical_url,
        description=f"{source.topic} · {source.audience}".strip(" ·"),
        provenance="retrieval",
    )


def _action(source: ApprovedSource) -> RecommendedAction:
    return RecommendedAction(
        id=f"open-{source.id}",
        label=f"Open {source.title}",
        href=source.canonical_url,
    )


def _from_source(source: ApprovedSource) -> tuple[SourceRef, RecommendedAction, Citation]:
    return (
        _source_ref(source),
        _action(source),
        Citation(url=source.canonical_url, title=source.title, quote=""),
    )


def find_program(arguments: dict[str, str], **_: object) -> NormalizedToolResult:
    found = list_sources(
        programs_only=True,
        audience=arguments.get("audience", ""),
        topic=arguments.get("topic", ""),
        keywords=arguments.get("keywords", ""),
    )
    if not found:
        return NormalizedToolResult(
            name="find_program",
            ok=True,
            status="not_found",
            user_message="I couldn't find a matching Cyber Florida program.",
            error_code="not_found",
        )
    sources, actions, citations = zip(*[_from_source(item) for item in found[:5]], strict=True)
    return NormalizedToolResult(
        name="find_program",
        ok=True,
        status="ok",
        user_message="I found approved Cyber Florida programs that match. You can open one below.",
        sources=sources,
        actions=actions,
        citations=citations,
        metadata={"count": str(len(found))},
    )


def find_resource(arguments: dict[str, str], **_: object) -> NormalizedToolResult:
    found = list_sources(
        programs_only=False,
        audience=arguments.get("audience", ""),
        topic=arguments.get("topic", ""),
        keywords=arguments.get("keywords", ""),
    )
    if not found:
        return NormalizedToolResult(
            name="find_resource",
            ok=True,
            status="not_found",
            user_message="I couldn't find a matching Cyber Florida resource.",
            error_code="not_found",
        )
    sources, actions, citations = zip(*[_from_source(item) for item in found[:5]], strict=True)
    return NormalizedToolResult(
        name="find_resource",
        ok=True,
        status="ok",
        user_message="I found approved Cyber Florida resources. You can open one below.",
        sources=sources,
        actions=actions,
        citations=citations,
        metadata={"count": str(len(found))},
    )


def search_approved_content(
    arguments: dict[str, str], *, retriever: Retriever | None = None, **_: object
) -> NormalizedToolResult:
    active = retriever if retriever is not None else fixture_retriever()
    hits = active.retrieve(arguments.get("query", ""))
    if not hits.available:
        return NormalizedToolResult(
            name="search_approved_content",
            ok=True,
            status="not_found",
            user_message="I couldn't find matching approved Cyber Florida content.",
            error_code="not_found",
        )
    sources: list[SourceRef] = []
    actions: list[RecommendedAction] = []
    citations: list[Citation] = []
    seen: set[str] = set()
    for chunk in hits.chunks:
        if chunk.access_class != "public" or chunk.url in seen:
            continue
        seen.add(chunk.url)
        source = get_source_by_id(chunk.source_id)
        if source is None or not source.active:
            continue
        sources.append(
            SourceRef(
                title=chunk.title,
                name="Cyber Florida",
                url=chunk.url,
                description=chunk.heading or chunk.title,
                provenance="retrieval",
            )
        )
        actions.append(
            RecommendedAction(
                id=f"open-{chunk.source_id}",
                label=f"Open {chunk.title}",
                href=chunk.url,
            )
        )
        citations.append(Citation(url=chunk.url, title=chunk.title, quote=chunk.content[:180]))
        if len(sources) >= 3:
            break
    if not sources:
        return NormalizedToolResult(
            name="search_approved_content",
            ok=True,
            status="not_found",
            user_message="I couldn't find matching approved Cyber Florida content.",
            error_code="not_found",
        )
    return NormalizedToolResult(
        name="search_approved_content",
        ok=True,
        status="ok",
        user_message="I found approved Cyber Florida content. You can open a source below.",
        sources=tuple(sources),
        actions=tuple(actions),
        citations=tuple(citations),
    )


def navigate_to_url(arguments: dict[str, str], **_: object) -> NormalizedToolResult:
    from pixel.knowledge.registry import get_approved_source

    source_id = arguments.get("source_id", "")
    url = arguments.get("url", "")
    source = get_source_by_id(source_id) if source_id else None
    if source is None and url:
        source = get_approved_source(url)
    target = source.canonical_url if source is not None else url
    ok, _reason = validate_navigation_url(target)
    if source is None or not ok:
        return NormalizedToolResult(
            name="navigate_to_url",
            ok=False,
            status="invalid_destination",
            user_message=(
                "I couldn't open that resource because the destination isn't on the approved list."
            ),
            error_code="invalid_destination",
        )
    ref, action, citation = _from_source(source)
    return NormalizedToolResult(
        name="navigate_to_url",
        ok=True,
        status="ok",
        user_message="I found the approved Cyber Florida page. You can open it below.",
        sources=(ref,),
        actions=(action,),
        citations=(citation,),
        metadata={"source_id": source.id},
    )


def register_production_tools(registry: ToolRegistry) -> None:
    common_lookup = {
        "audience": "enum_audience",
        "topic": "string",
        "keywords": "string",
    }
    registry.register(
        ToolDefinition(
            name="find_program",
            description="Find approved Cyber Florida programs by audience, topic, or keywords.",
            version="1.0.0",
            permission="public",
            confirmation_policy="none",
            side_effect_level="none",
            timeout_seconds=DEFAULT_TIMEOUT,
            input_fields=common_lookup,
            required_fields=(),
            allowed_domains=("cyberflorida.org", "www.cyberflorida.org"),
            audit=True,
            handler=find_program,
        )
    )
    registry.register(
        ToolDefinition(
            name="find_resource",
            description="Find approved Cyber Florida public resources.",
            version="1.0.0",
            permission="public",
            confirmation_policy="none",
            side_effect_level="none",
            timeout_seconds=DEFAULT_TIMEOUT,
            input_fields=common_lookup,
            required_fields=(),
            allowed_domains=("cyberflorida.org", "www.cyberflorida.org"),
            audit=True,
            handler=find_resource,
        )
    )
    registry.register(
        ToolDefinition(
            name="search_approved_content",
            description="Search the approved Cyber Florida knowledge index only.",
            version="1.0.0",
            permission="public",
            confirmation_policy="none",
            side_effect_level="none",
            timeout_seconds=DEFAULT_TIMEOUT,
            input_fields={"query": "string"},
            required_fields=("query",),
            allowed_domains=("cyberflorida.org", "www.cyberflorida.org"),
            audit=True,
            handler=search_approved_content,
        )
    )
    registry.register(
        ToolDefinition(
            name="navigate_to_url",
            description="Resolve an approved Cyber Florida canonical URL for the user to open.",
            version="1.0.0",
            permission="public",
            confirmation_policy="ui_click",
            side_effect_level="navigation",
            timeout_seconds=DEFAULT_TIMEOUT,
            input_fields={"url": "string", "source_id": "string"},
            required_fields=(),
            allowed_domains=("cyberflorida.org", "www.cyberflorida.org"),
            audit=True,
            handler=navigate_to_url,
        )
    )
