# Security overview (Phase 0)

Pixel will represent a cybersecurity organization. Users will over-trust it. Phase 8 runtime controls are documented in [threat-model.md](threat-model.md) and [security-review.md](security-review.md). This file keeps the original Phase 0 decisions.

## Trust boundaries (planned)

```
User device --TLS--> Pixel web origin
                         |
                         | session token, never provider keys
                         v
                    Pixel API
                   /    |     \
            Postgres  Vendors  Allowlisted fetch (worker)
```

## Assets

Provider keys; system policy; Cyber Florida factual integrity; user audio/transcripts; tool execution; admin ingestion; availability/cost.

## Priority threats

| Threat | Phase 0 control decision |
|---|---|
| Prompt injection (user + RAG) | Untrusted evidence channel; tools not granted by documents |
| Secret leak to browser or git | No keys in client; no secrets in repo; `.env.example` names only (when added) |
| Open admin ingestion | Fail closed without authz |
| Hallucinated org facts | Retrieval required; abstain if weak |
| Offensive cyber assistance | Policy refuse (SEC-14) |
| Audio retention | Transient STT; no default recording archive |
| XSS from model/RAG text | Encode as text; never raw HTML |
| Session guessing | High-entropy session IDs |

## Explicit non-goals for the assistant

Pixel must not help with exploits, malware, unauthorized access, or attack procedures, including roleplay and “authorized lab/CTF” framing.

Full control list: `docs/SECURITY.md`. Implementation mapping: Phase 8 in `docs/ROADMAP.md`.
