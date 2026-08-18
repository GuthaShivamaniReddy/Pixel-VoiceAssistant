from dataclasses import replace

from pixel.knowledge import UnavailableRetriever
from pixel.knowledge.embeddings import HashEmbeddingProvider
from pixel.knowledge.ingest import ingest_fixtures
from pixel.knowledge.retrieve import KnowledgeRetriever, retrieval_query
from pixel.knowledge.runtime import fixture_retriever
from pixel.knowledge.store import InMemoryKnowledgeStore
from pixel.orchestrator.fallbacks import ORG_ABSTAIN
from pixel.orchestrator.process import OrchestratorConfig, process_turn
from pixel.providers.mock import MockLLM, MockTextToSpeech
from pixel.shared.cancellation import CancellationFlag


def _retriever() -> KnowledgeRetriever:
    return fixture_retriever()


def test_relevant_query_returns_expected_source() -> None:
    hits = _retriever().retrieve("What is FirstLine at Cyber Florida?")
    assert hits.available
    assert any(chunk.source_id == "cf-firstline" for chunk in hits.chunks[:5])


def test_unrelated_query_has_no_acceptable_hits() -> None:
    hits = _retriever().retrieve("pasta recipe carbonara parmesan")
    assert hits.available is False
    assert hits.chunks == ()


def test_inactive_source_is_not_retrieved() -> None:
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    ingest_fixtures(embedder=embedder, store=store)
    store.deactivate_source("cf-firstline")
    retriever = KnowledgeRetriever(store, embedder)
    hits = retriever.retrieve("What is FirstLine public-sector training?")
    assert all(chunk.source_id != "cf-firstline" for chunk in hits.chunks)


def test_caller_cannot_override_access_class_to_internal() -> None:
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    ingest_fixtures(embedder=embedder, store=store)
    retriever = KnowledgeRetriever(store, embedder)
    sample = next(iter(store.chunks.values()))
    privileged = replace(
        sample,
        chunk_id="internal-bypass",
        source_id="cf-internal",
        access_class="internal",
        content="Internal privileged Cyber Florida budget figure 999",
        active=True,
    )
    store.chunks[privileged.chunk_id] = privileged
    hits = retriever.retrieve(
        "Internal privileged Cyber Florida budget figure",
        access_class="internal",
    )
    assert all(chunk.access_class == "public" for chunk in hits.chunks)
    assert all(chunk.chunk_id != "internal-bypass" for chunk in hits.chunks)


def test_suspicious_sql_shaped_query_does_not_break_retrieval() -> None:
    hits = _retriever().retrieve("What is FirstLine'; DROP TABLE knowledge_chunks; --")
    assert hits.reason in {"ok", "no_acceptable_evidence", "insufficient_evidence"}


def test_privileged_chunks_are_not_mixed_into_public_search() -> None:
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    ingest_fixtures(embedder=embedder, store=store)
    retriever = KnowledgeRetriever(store, embedder)
    sample = next(iter(store.chunks.values()))
    privileged = replace(
        sample,
        chunk_id="internal-only",
        source_id="cf-internal",
        access_class="internal",
        content="Internal privileged Cyber Florida budget figure 999",
        active=True,
    )
    store.chunks[privileged.chunk_id] = privileged
    hits = retriever.retrieve("Internal privileged Cyber Florida budget figure")
    assert all(chunk.access_class == "public" for chunk in hits.chunks)
    assert all(chunk.chunk_id != "internal-only" for chunk in hits.chunks)


def test_follow_up_query_includes_prior_user_turn() -> None:
    query = retrieval_query(
        "Tell me more about the second one.",
        (("user", "What programs does Cyber Florida offer for students?"),),
    )
    assert "students" in query.lower()
    assert "second one" in query.lower()


def test_org_question_requires_retrieval_and_returns_citation() -> None:
    outcome = process_turn(
        text="What is Cyber Florida?",
        llm=MockLLM(),
        tts=MockTextToSpeech(),
        cancellation=CancellationFlag(),
        speak=False,
        config=OrchestratorConfig(max_attempts=1, backoff_seconds=0),
    )
    assert outcome.retrieval and outcome.retrieval.required and outcome.retrieval.executed
    assert outcome.response.sources
    assert outcome.response.sources[0].provenance == "retrieval"
    assert outcome.response.citations
    assert outcome.timings.retrieval_latency_ms is not None
    assert "Florida Center for Cybersecurity" in outcome.response.text


def test_missing_evidence_abstains() -> None:
    outcome = process_turn(
        text="When is the 2027 Cyber Florida student conference?",
        llm=MockLLM(),
        tts=MockTextToSpeech(),
        cancellation=CancellationFlag(),
        speak=False,
        config=OrchestratorConfig(max_attempts=1, backoff_seconds=0),
        retriever=UnavailableRetriever(),
    )
    assert outcome.retrieval and outcome.retrieval.available is False
    assert outcome.response.safety_state == "abstained"
    text = outcome.response.text
    assert "cannot verify" in text.lower() or ORG_ABSTAIN[:20] in text


def test_retrieved_injection_cannot_override_policy() -> None:
    store = InMemoryKnowledgeStore()
    embedder = HashEmbeddingProvider()
    ingest_fixtures(embedder=embedder, store=store, include_injection=True)
    retriever = KnowledgeRetriever(store, embedder)
    outcome = process_turn(
        text="What is Cyber Florida?",
        llm=MockLLM(),
        tts=MockTextToSpeech(),
        cancellation=CancellationFlag(),
        speak=False,
        config=OrchestratorConfig(max_attempts=1, backoff_seconds=0),
        retriever=retriever,
    )
    text = outcome.response.text.lower()
    assert "you are pixel, cyber florida" not in text
    assert "admin tool" not in text
    assert "api key" not in text
    assert "system prompt" not in text
