import os

import pytest

from pixel.knowledge.embeddings import HashEmbeddingProvider
from pixel.knowledge.fixtures import fixture_html
from pixel.knowledge.ingest import ingest_html
from pixel.knowledge.migrate import downgrade, upgrade
from pixel.knowledge.postgres import PostgresKnowledgeStore
from pixel.knowledge.registry import PUBLIC_SOURCES
from pixel.knowledge.retrieve import KnowledgeRetriever

DATABASE_URL = os.environ.get("PIXEL_TEST_DATABASE_URL", "")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="PIXEL_TEST_DATABASE_URL is not set",
)


def test_postgres_upgrade_downgrade_and_search() -> None:
    upgrade(DATABASE_URL)
    store = PostgresKnowledgeStore(DATABASE_URL)
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-about")
    ingest_html(source, fixture_html("about"), embedder=HashEmbeddingProvider(), store=store)
    retriever = KnowledgeRetriever(store, HashEmbeddingProvider())
    hits = retriever.retrieve("What is Cyber Florida?")
    assert hits.available
    store.deactivate_source("cf-about")
    hidden = retriever.retrieve("What is Cyber Florida?")
    assert all(chunk.source_id != "cf-about" for chunk in hidden.chunks)
    downgrade(DATABASE_URL)
    upgrade(DATABASE_URL)
    downgrade(DATABASE_URL)
