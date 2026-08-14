import httpx
import pytest

from pixel.knowledge.embeddings import HashEmbeddingProvider, OpenAIEmbeddingProvider
from pixel.knowledge.fixtures import fixture_html
from pixel.knowledge.ingest import ingest_approved_url, ingest_fixtures, ingest_html
from pixel.knowledge.registry import PUBLIC_SOURCES, require_approved_url
from pixel.knowledge.store import InMemoryKnowledgeStore
from pixel.providers.errors import ProviderError


def test_unapproved_url_is_rejected() -> None:
    try:
        require_approved_url("https://example.com/about")
    except ValueError as exc:
        assert "allowlist" in str(exc).lower()
    else:
        raise AssertionError("expected rejection")


def test_ingest_html_indexes_approved_fixture() -> None:
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-about")
    store = InMemoryKnowledgeStore()
    result = ingest_html(
        source, fixture_html("about"), embedder=HashEmbeddingProvider(), store=store
    )
    assert result.status == "indexed"
    assert result.chunk_count > 0
    assert store.get_source("cf-about") is not None


def test_unchanged_content_skips_reembed() -> None:
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-home")
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    first = ingest_html(source, fixture_html("home"), embedder=embedder, store=store)
    second = ingest_html(source, fixture_html("home"), embedder=embedder, store=store)
    assert first.status == "indexed"
    assert second.unchanged is True
    assert second.version == first.version


def test_changed_content_creates_new_version() -> None:
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-home")
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    first = ingest_html(source, fixture_html("home"), embedder=embedder, store=store)
    changed = fixture_html("home").replace(
        "outreach for the state of Florida",
        "statewide outreach",
    )
    second = ingest_html(source, changed, embedder=embedder, store=store)
    assert second.unchanged is False
    assert second.version == first.version + 1


def test_parse_failure_keeps_previous_version() -> None:
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-about")
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    first = ingest_html(source, fixture_html("about"), embedder=embedder, store=store)
    failed = ingest_html(source, "<html><body></body></html>", embedder=embedder, store=store)
    assert failed.status == "failed"
    assert store.get_source("cf-about") is not None
    record = store.get_source("cf-about")
    assert record is not None
    assert record.version == first.version
    assert any(chunk.source_id == "cf-about" and chunk.active for chunk in store.chunks.values())


def test_empty_content_is_not_success() -> None:
    source = next(item for item in PUBLIC_SOURCES if item.id == "cf-events")
    result = ingest_html(
        source,
        "<html><nav>menu</nav></html>",
        embedder=HashEmbeddingProvider(),
        store=InMemoryKnowledgeStore(),
    )
    assert result.status == "failed"
    assert result.chunk_count == 0


def test_ingest_approved_url_requires_registry() -> None:
    store = InMemoryKnowledgeStore()
    try:
        ingest_approved_url(
            "https://not-cyberflorida.example/page",
            fixture_html("home"),
            embedder=HashEmbeddingProvider(),
            store=store,
        )
    except ValueError:
        assert store.chunks == {}
    else:
        raise AssertionError("expected allowlist error")


def test_ingest_fixtures_loads_public_corpus() -> None:
    store = InMemoryKnowledgeStore()
    results = ingest_fixtures(embedder=HashEmbeddingProvider(), store=store)
    assert len(results) == len([item for item in PUBLIC_SOURCES if item.fixture_key])
    assert all(item.status in {"indexed", "unchanged"} for item in results)


def test_hash_embedding_has_expected_dimensions() -> None:
    vector = HashEmbeddingProvider().embed_query("Cyber Florida FirstLine")
    assert len(vector) == 1536
    batch = HashEmbeddingProvider().embed_documents(["one", "two"])
    assert len(batch) == 2


def test_empty_embedding_fails() -> None:
    with pytest.raises(ProviderError):
        HashEmbeddingProvider().embed_query("   ")


def test_openai_embedding_malformed_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": [1.0]}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAIEmbeddingProvider("sk-test", dimensions=1536, client=client)
    with pytest.raises(ProviderError):
        provider.embed_query("Cyber Florida")
