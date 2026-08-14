"""Cyber Florida knowledge ingestion and retrieval."""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from pixel.knowledge.models import RetrievalHitSet, RetrievedChunk


@runtime_checkable
class Retriever(Protocol):
    def retrieve(self, query: str, *, top_k: int | None = None) -> RetrievalHitSet: ...


class UnavailableRetriever:
    def retrieve(self, query: str, *, top_k: int | None = None) -> RetrievalHitSet:
        del query, top_k
        return RetrievalHitSet(
            available=False,
            chunks=(),
            reason="retrieval_unavailable",
            query="",
        )


@runtime_checkable
class VectorStoreProvider(Protocol):
    provider_id: str

    def upsert(self, records: Sequence[object]) -> None: ...

    def search(self, query_embedding: object, *, limit: int) -> Sequence[object]: ...

    def delete_by_source(self, source_id: str) -> None: ...


def fixture_retriever(*, include_injection: bool = False):
    from pixel.knowledge.runtime import fixture_retriever as _inner

    return _inner(include_injection=include_injection)


__all__ = [
    "RetrievalHitSet",
    "RetrievedChunk",
    "Retriever",
    "UnavailableRetriever",
    "VectorStoreProvider",
    "fixture_retriever",
]
