# Pixel — Knowledge ingestion and RAG (Phase 6)

**Status:** Implemented for the approved public Cyber Florida corpus. Local and CI use a governed HTML fixture index plus deterministic hash embeddings. PostgreSQL + pgvector is implemented and used when `PIXEL_TEST_DATABASE_URL` / a migrated database is available.

Pixel answers organization-specific questions from **approved, traceable sources**. It does not treat model memory as Cyber Florida fact.

```text
approved source → registry → fetch/import → extract → normalize →
semantic chunk → embed → store → retrieve → evidence →
orchestrator → grounded answer → citation
```

If evidence is missing or below the relevance floor, Pixel **abstains**.

## Approved source registry

Authoritative sources are the explicit allowlist in `packages/pixel/pixel/knowledge/registry.py`.

- HTTPS `cyberflorida.org` / `www.cyberflorida.org` only.
- Each source is registered with `id`, title, canonical URL, `source_type`, `access_class`, topic, audience, and fixture key.
- Arbitrary URLs cannot be ingested. User-provided URLs never become trusted knowledge.
- There is **no open-web crawl**.

Phase 6 indexes **public** pages only. No fake internal corpus is created. Retrieval always filters `access_class=public`. Privileged chunks cannot appear in the public index.

## Ingestion

`ingest_html` / `ingest_approved_url` / `ingest_fixtures`:

1. Reject URLs that are not on the allowlist.
2. Extract HTML (stdlib parser). Skip `nav`/`footer`/`script`/`style` and cookie/menu boilerplate. Keep headings, paragraphs, and lists.
3. Normalize whitespace/encoding (NFKC). Do not rewrite facts.
4. Hash normalized document text (`sha256`). Unchanged hash → skip re-embed.
5. Semantic chunk on heading/section boundaries (1200 character secondary cap).
6. Stable chunk ids: `sha256(source_id|heading_path|normalized_body)[:24]`.
7. Embed via `EmbeddingProvider` (`embed_documents` / `embed_query`).
8. Replace that source’s active chunks. Prior valid chunks remain if parse/fetch fails.

PDF and DOCX importers are **not required**: the approved inventory is public HTML pages.

Failed parse/empty content is recorded as `status=failed`. The last good version stays retrievable.

Worker: `pixel-worker ingest` indexes the fixture corpus (no admin UI; admin remains fail-closed).

Live fetch (`fetch_approved_html`) uses the **canonical allowlisted URL** only, does not follow redirects, and is not a crawl.

## Document versioning

Each successful change increments `version` and writes a new `document_id` (`{source_id}-v{n}`). Chunks point at source + document version. Deactivation sets `active=false` on the source and its chunks. History is retained; normal retrieval uses `active_only=True`.

## Embeddings

| Mode | Provider | Model | Dimensions |
|---|---|---|---|
| Local / CI | `HashEmbeddingProvider` | `hash-bow-v1` | 1536 |
| Vendor | `OpenAIEmbeddingProvider` | `text-embedding-3-small` (configurable) | 1536 |

Do not change embedding model/dimensions without rebuilding the index. Vendor SDK calls stay inside the adapter.

## Vector storage

- **Default:** in-memory store seeded from fixtures at API start (`fixture_retriever()`), so text/voice work without Docker. `KNOWLEDGE_STORE` and `EMBEDDING_PROVIDER` are documented for operators; the API process still uses the fixture index unless a future runtime switch is wired. Do not assume Postgres is queried because the env var is set.
- **Postgres + pgvector:** tables `knowledge_sources`, `knowledge_documents`, `knowledge_chunks` (`vector(1536)`). Migration: `pixel.knowledge.migrate.upgrade`. IVFFlat is **not** used yet (empty/small corpus). Metadata indexes: `(active, access_class)`, `source_id`.

Reranking is **not used**. Baseline retrieval is cosine similarity + `top_k` + `min_score`. Add rerank only if evaluation shows a real gain.

## Retrieval

`KnowledgeRetriever.search(query, filters, top_k)` returns `RetrievedChunk` values (not raw DB rows).

Filters: active sources only, `access_class`, configurable `top_k` (default 5), `min_score` (default 0.08).

Follow-up queries use the current question plus the prior user turn when the utterance is referential (`tell me more`, `the second one`, `what about beginners`). Full history is not dumped into the vector query.

Scores below `min_score` are not evidence.

## Orchestrator grounding

For `cyberflorida_knowledge`:

1. Intent router sets `requires_retrieval=True`.
2. Retriever runs. Organization facts **cannot** skip retrieval.
3. No acceptable hits → canned abstention (`ORG_ABSTAIN`). The model is not asked to guess.
4. Hits → evidence is passed on `LlmRequest.evidence` inside `BEGIN/END UNTRUSTED RETRIEVED DOCUMENT` delimiters, labeled as data not instructions.
5. Citations/`SourceRef` come from retrieved chunks (`provenance=retrieval`). Source cards show “Approved Cyber Florida source”.
6. Retrieved text cannot grant tools, change policy, or become executable navigation (Phase 7).

Prompt-injection text inside a document is treated as document content. Mock and policy both ignore instruction-like sentences.

## Freshness and conflicts

Dates, events, leadership, contacts, eligibility, and schedules must come from current indexed evidence. If the corpus has no current fact, Pixel abstains.

If approved sources conflict, Pixel does not silently pick a winner. Both chunks may appear in `top_k`; policy tells the model to surface uncertainty and prefer the most current listed evidence. There is no separate freshness reranker in Phase 6.

## Evaluation

Dataset: `evals/knowledge/cases.jsonl` (100+ questions). Runner: `pixel.knowledge.evaluate.evaluate`.

Measures Hit@1/3/5, context precision, groundedness, answer correctness, citation correctness, abstention, freshness, retrieval latency p50/p95.

## Security / privacy

- Parameterized SQL in the Postgres store.
- No user conversations, passwords, or tokens in the knowledge index.
- Embeddings and chunk text are not exposed on a public search API.
- Ingestion is a worker/CLI action, not an anonymous HTTP endpoint.

## Environment

See `.env.example`: `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `KNOWLEDGE_STORE`, `RETRIEVAL_TOP_K`, `RETRIEVAL_MIN_SCORE`, `DATABASE_URL`.
