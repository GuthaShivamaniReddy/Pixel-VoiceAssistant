"""Build a fixture-backed retriever for local/API use."""

from __future__ import annotations

from pixel.knowledge.embeddings import HashEmbeddingProvider
from pixel.knowledge.ingest import ingest_fixtures
from pixel.knowledge.retrieve import KnowledgeRetriever
from pixel.knowledge.store import InMemoryKnowledgeStore

_CACHE: KnowledgeRetriever | None = None


def fixture_retriever(*, include_injection: bool = False) -> KnowledgeRetriever:
    global _CACHE
    if _CACHE is not None and not include_injection:
        return _CACHE
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    ingest_fixtures(embedder=embedder, store=store, include_injection=include_injection)
    retriever = KnowledgeRetriever(store, embedder)
    if not include_injection:
        _CACHE = retriever
    return retriever


def reset_retriever_cache() -> None:
    global _CACHE
    _CACHE = None
