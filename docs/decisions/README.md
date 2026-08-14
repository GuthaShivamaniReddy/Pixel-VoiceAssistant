# Architecture Decision Records

ADRs record choices that later phases must not silently reverse.

| ID | Decision | Status |
|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith: Next.js + FastAPI + Postgres/pgvector | Accepted (foundation implemented) |
| [0002](0002-provider-interfaces.md) | Provider interfaces for LLM, STT, TTS, embeddings, vector store | Accepted (interfaces only) |
| [0003](0003-websocket-ptt-first.md) | WebSocket + push-to-talk before WebRTC | Accepted (planned) |
| [0004](0004-untrusted-rag.md) | Retrieved content is untrusted; RAG required for org facts | Accepted |
| [0005](0005-postgres-sessions.md) | PostgreSQL sessions first; Redis later if measured | Accepted (Compose Postgres; no session tables yet) |
| [0006](0006-public-sessions-admin-fail-closed.md) | Anonymous public Q&A; admin fail-closed until SSO | Accepted (admin 403) |
| [0007](0007-mock-providers-local.md) | Mock providers default in local development | Accepted (production rejects mock) |
| [0008](0008-orchestrator-boundary.md) | Central `process_turn` orchestrator; versioned server policy | Accepted |
| [0009](0009-conversation-state.md) | Bounded in-memory sessions with TTL and clear | Accepted |
| [0010](0010-intent-routing.md) | Deterministic six-intent taxonomy | Accepted |
| [0011](0011-knowledge-rag.md) | Fixture corpus, hash embeddings, no rerank for Phase 6 | Accepted |

Template: [adr-template.md](adr-template.md).

**Reality check:** Phases 2–6 are implemented in the working tree. Production tools are not implemented.
