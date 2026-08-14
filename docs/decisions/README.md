# Architecture Decision Records

ADRs record choices that later phases must not silently reverse.

| ID | Decision | Status |
|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith: Next.js + FastAPI + Postgres/pgvector | Accepted (planned) |
| [0002](0002-provider-interfaces.md) | Provider interfaces for LLM, STT, TTS, embeddings, vector store | Accepted (planned) |
| [0003](0003-websocket-ptt-first.md) | WebSocket + push-to-talk before WebRTC | Accepted (planned) |
| [0004](0004-untrusted-rag.md) | Retrieved content is untrusted; RAG required for org facts | Accepted |
| [0005](0005-postgres-sessions.md) | PostgreSQL sessions first; Redis later if measured | Accepted (planned) |
| [0006](0006-public-sessions-admin-fail-closed.md) | Anonymous public Q&A; admin fail-closed until SSO | Accepted |
| [0007](0007-mock-providers-local.md) | Mock providers default in local development | Accepted (planned) |

Template: [adr-template.md](adr-template.md).

**Reality check:** These decisions are binding for upcoming implementation. They are not evidenced by running code.
