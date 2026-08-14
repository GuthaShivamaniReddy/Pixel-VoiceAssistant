"""In-memory knowledge index used for tests and local runs without Postgres."""

from __future__ import annotations

from time import perf_counter
from typing import Protocol, runtime_checkable

from pixel.knowledge.embeddings import cosine
from pixel.knowledge.models import IndexedChunk, RetrievalHitSet, RetrievedChunk, SourceRecord


@runtime_checkable
class KnowledgeStore(Protocol):
    def upsert_source(self, source: SourceRecord) -> None: ...

    def get_source(self, source_id: str) -> SourceRecord | None: ...

    def replace_chunks(self, source_id: str, chunks: list[IndexedChunk]) -> None: ...

    def deactivate_source(self, source_id: str) -> None: ...

    def search(
        self,
        query_embedding: tuple[float, ...],
        *,
        top_k: int,
        min_score: float,
        access_class: str,
        active_only: bool,
    ) -> RetrievalHitSet: ...


class InMemoryKnowledgeStore:
    def __init__(self) -> None:
        self.sources: dict[str, SourceRecord] = {}
        self.chunks: dict[str, IndexedChunk] = {}

    def upsert_source(self, source: SourceRecord) -> None:
        self.sources[source.id] = source

    def get_source(self, source_id: str) -> SourceRecord | None:
        return self.sources.get(source_id)

    def replace_chunks(self, source_id: str, chunks: list[IndexedChunk]) -> None:
        stale = [key for key, chunk in self.chunks.items() if chunk.source_id == source_id]
        for key in stale:
            del self.chunks[key]
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk

    def deactivate_source(self, source_id: str) -> None:
        source = self.sources.get(source_id)
        if source is None:
            return
        source.active = False
        source.status = "inactive"
        for chunk in self.chunks.values():
            if chunk.source_id == source_id:
                chunk.active = False

    def search(
        self,
        query_embedding: tuple[float, ...],
        *,
        top_k: int,
        min_score: float,
        access_class: str,
        active_only: bool,
    ) -> RetrievalHitSet:
        started = perf_counter()
        scored: list[RetrievedChunk] = []
        for chunk in self.chunks.values():
            if active_only and not chunk.active:
                continue
            source = self.sources.get(chunk.source_id)
            if source is not None and not source.active:
                continue
            if chunk.access_class != access_class:
                continue
            score = cosine(query_embedding, chunk.embedding)
            if score < min_score:
                continue
            scored.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    score=score,
                    source_id=chunk.source_id,
                    document_id=chunk.document_id,
                    title=chunk.title,
                    url=chunk.url,
                    heading=chunk.heading_path,
                    access_class=chunk.access_class,
                    version=chunk.version,
                    metadata={"topic": chunk.topic, "audience": chunk.audience},
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        hits = tuple(scored[:top_k])
        available = bool(hits)
        reason = "ok" if available else "no_acceptable_evidence"
        return RetrievalHitSet(
            available=available,
            chunks=hits,
            reason=reason,
            query="",
            latency_ms=int((perf_counter() - started) * 1000),
        )
