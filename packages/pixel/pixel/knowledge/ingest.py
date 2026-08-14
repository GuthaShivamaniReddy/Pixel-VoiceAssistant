"""Ingest approved HTML into the knowledge store."""

from __future__ import annotations

from uuid import uuid4

from pixel.ai import EmbeddingProvider
from pixel.domain import utcnow
from pixel.knowledge.chunking import chunk_blocks
from pixel.knowledge.fixtures import fixture_html
from pixel.knowledge.html import extract_html
from pixel.knowledge.models import ApprovedSource, IndexedChunk, IngestResult, SourceRecord
from pixel.knowledge.normalize import content_hash, normalize_text
from pixel.knowledge.registry import PUBLIC_SOURCES, require_approved_url
from pixel.knowledge.store import KnowledgeStore


def ingest_html(
    source: ApprovedSource,
    html: str,
    *,
    embedder: EmbeddingProvider,
    store: KnowledgeStore,
) -> IngestResult:
    existing = store.get_source(source.id)
    try:
        title, blocks = extract_html(html)
    except ValueError as exc:
        record = existing or SourceRecord(
            id=source.id,
            title=source.title,
            canonical_url=source.canonical_url,
            source_type=source.source_type,
            access_class=source.access_class,
            topic=source.topic,
            audience=source.audience,
            active=True,
            status="failed",
            content_hash="",
            version=0,
            error=str(exc),
        )
        record.status = "failed"
        record.error = str(exc)
        store.upsert_source(record)
        return IngestResult(
            source_id=source.id,
            status="failed",
            version=record.version,
            content_hash=record.content_hash,
            chunk_count=0,
            unchanged=False,
            error=str(exc),
        )

    title = title or source.title
    joined = normalize_text("\n".join(text for _, text in blocks))
    digest = content_hash(joined)
    if existing and existing.content_hash == digest and existing.status == "active":
        existing.last_fetched_at = utcnow()
        store.upsert_source(existing)
        return IngestResult(
            source_id=source.id,
            status="unchanged",
            version=existing.version,
            content_hash=digest,
            chunk_count=0,
            unchanged=True,
        )

    pieces = chunk_blocks(blocks, source_id=source.id, title=title)
    embeddings = list(embedder.embed_documents([str(item["content"]) for item in pieces]))
    version = (existing.version + 1) if existing else 1
    document_id = f"{source.id}-v{version}"
    now = utcnow()
    indexed: list[IndexedChunk] = []
    for piece, embedding in zip(pieces, embeddings, strict=True):
        indexed.append(
            IndexedChunk(
                chunk_id=str(piece["chunk_id"]),
                document_id=document_id,
                source_id=source.id,
                ordinal=int(piece["ordinal"]),
                heading_path=str(piece["heading_path"]),
                content=str(piece["content"]),
                content_hash=str(piece["content_hash"]),
                token_count=int(piece["token_count"]),
                title=title,
                url=source.canonical_url,
                topic=source.topic,
                audience=source.audience,
                source_type=source.source_type,
                access_class=source.access_class,
                version=version,
                active=True,
                embedding=tuple(float(value) for value in embedding),
                indexed_at=now,
            )
        )
    record = SourceRecord(
        id=source.id,
        title=title,
        canonical_url=source.canonical_url,
        source_type=source.source_type,
        access_class=source.access_class,
        topic=source.topic,
        audience=source.audience,
        active=True,
        status="active",
        content_hash=digest,
        version=version,
        last_fetched_at=now,
        last_updated_at=now,
        error=None,
    )
    store.upsert_source(record)
    store.replace_chunks(source.id, indexed)
    return IngestResult(
        source_id=source.id,
        status="indexed",
        version=version,
        content_hash=digest,
        chunk_count=len(indexed),
        unchanged=False,
    )


def ingest_approved_url(
    url: str, html: str, *, embedder: EmbeddingProvider, store: KnowledgeStore
) -> IngestResult:
    source = require_approved_url(url)
    return ingest_html(source, html, embedder=embedder, store=store)


def ingest_fixtures(
    *, embedder: EmbeddingProvider, store: KnowledgeStore, include_injection: bool = False
) -> list[IngestResult]:
    results: list[IngestResult] = []
    for source in PUBLIC_SOURCES:
        if not source.fixture_key:
            continue
        results.append(
            ingest_html(
                source,
                fixture_html(source.fixture_key),
                embedder=embedder,
                store=store,
            )
        )
    if include_injection:
        about = next(item for item in PUBLIC_SOURCES if item.id == "cf-about")
        results.append(
            ingest_html(about, fixture_html("injection"), embedder=embedder, store=store)
        )
    return results


def new_job_id() -> str:
    return str(uuid4())
