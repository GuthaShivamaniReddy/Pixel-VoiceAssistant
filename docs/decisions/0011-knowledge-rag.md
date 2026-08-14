# ADR-0011: Fixture corpus, hash embeddings, and no rerank for Phase 6

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering (Phase 6 implementation)

## Context

Phase 6 must retrieve approved Cyber Florida knowledge with traceable citations. Docker Postgres is not always available in local/CI. Live OpenAI embeddings are not the default. The approved source inventory is a small set of public HTML pages.

## Decision

1. Register sources explicitly. Do not crawl. Do not trust user URLs.
2. Ship a governed HTML fixture corpus that mirrors the allowlisted public pages for local/CI.
3. Use deterministic hash bag-of-words embeddings (1536-d) when `EMBEDDING_PROVIDER=mock`.
4. Implement PostgreSQL + pgvector as the production-shaped store; default the API to the in-memory fixture index so voice/text keep working without Docker.
5. Do not add reranking until evaluation shows a measured gain over cosine + `min_score`.
6. PDF/DOCX parsers are out of scope until an approved non-HTML source is registered.

## Consequences

- Local RAG is real cosine retrieval over fixture embeddings, not a keyword stub.
- Live cyberflorida.org fetch and OpenAI embeddings remain optional and untested without keys/network.
- Hash embeddings are weaker than vendor embeddings; Hit@k is measured honestly against the fixture corpus.

## Alternatives considered

- Require Postgres for every test: rejected; breaks local/CI when Docker is down.
- Keyword-only retriever: rejected; Phase 6 forbids completely mocked retrieval.
- Auto rerank: rejected until baseline eval exists.
