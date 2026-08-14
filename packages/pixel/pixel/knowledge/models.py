"""Knowledge models. Chunks always trace to a document version and source."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pixel.domain import utcnow


@dataclass(frozen=True)
class ApprovedSource:
    id: str
    title: str
    canonical_url: str
    source_type: str
    access_class: str
    topic: str
    audience: str
    active: bool = True
    fixture_key: str | None = None


@dataclass
class SourceRecord:
    id: str
    title: str
    canonical_url: str
    source_type: str
    access_class: str
    topic: str
    audience: str
    active: bool
    status: str
    content_hash: str
    version: int
    last_fetched_at: datetime | None = None
    last_updated_at: datetime | None = None
    publication_date: str | None = None
    error: str | None = None


@dataclass
class DocumentVersion:
    id: str
    source_id: str
    version: int
    title: str
    canonical_url: str
    content_hash: str
    status: str
    fetched_at: datetime
    normalized_text: str
    access_class: str
    topic: str
    audience: str
    source_type: str


@dataclass
class IndexedChunk:
    chunk_id: str
    document_id: str
    source_id: str
    ordinal: int
    heading_path: str
    content: str
    content_hash: str
    token_count: int
    title: str
    url: str
    topic: str
    audience: str
    source_type: str
    access_class: str
    version: int
    active: bool
    embedding: tuple[float, ...]
    indexed_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    source_id: str
    document_id: str
    title: str
    url: str
    heading: str
    access_class: str
    version: int
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalHitSet:
    available: bool
    chunks: tuple[RetrievedChunk, ...]
    reason: str
    query: str
    latency_ms: int = 0


@dataclass(frozen=True)
class IngestResult:
    source_id: str
    status: str
    version: int
    content_hash: str
    chunk_count: int
    unchanged: bool
    error: str | None = None
