# Pixel — Requirements Gap Analysis

**Assessed:** 2026-08-14  
**Specification:** `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` v1.0  
**Method:** Recursive repository inspection. Documentation is **not** treated as implementation.

**Repository reality (Phase 0 snapshot):** At assessment time there was **no application**. This file is a historical Phase 0 inspection. Phases 2–3 later added `apps/`, packages, tests, CI, Docker, and a mocked conversation UI. Do not read the tables below as current runtime status.

Status key:

| Status | Meaning |
|---|---|
| COMPLETE | Implemented, verified in code |
| PARTIAL | Some code or docs exist; capability does not meet the spec |
| MISSING | Not implemented |
| BROKEN | Implemented but fails the spec |
| NEEDS VERIFICATION | Code exists but was not proven in this pass |
| DEFERRED BY SPECIFICATION | Explicitly out of MVP / later release |

---

## 1. Platform layers

| Layer | Spec expectation | Status | Notes |
|---|---|---|---|
| Client / UX | TypeScript React/Next.js | MISSING | No frontend |
| Realtime voice transport | WebRTC or WebSocket | MISSING | Planned: WebSocket + PTT (`docs/architecture.md`) |
| Speech processing | STT, TTS, VAD, barge-in | MISSING | Interfaces designed only |
| AI orchestration | Intent, context, policy, validation | MISSING | |
| Cyber Florida RAG | Allowlisted ingest + pgvector | MISSING | |
| Tools / actions | Allowlisted navigation/lookup | MISSING | |
| Data / sessions | Postgres sessions, no raw audio | MISSING | Schema designed only |
| Security / authorization | Server-side authz, injection controls | MISSING | Policy docs only |
| Observability | Correlation IDs, stage metrics | MISSING | |
| Administration | Authz ingestion/reindex | MISSING | Must fail closed when built |
| Testing / evaluation | Unit, E2E, RAG, safety evals | MISSING | Strategy docs only |
| CI/CD / deploy | Compose, env promotion | MISSING | |
| Provider adapters | LLM/STT/TTS/embed/vector | MISSING | Contracts in architecture doc |

---

## 2. Functional requirements

| ID | Requirement | Status | Affected area (future) | Dependency | Security | Priority | Testing |
|---|---|---|---|---|---|---|---|
| FR-01 | Voice capture | MISSING | `apps/web` | Mic permission UX | Capture only after explicit start | P0 | E2E + unit state machine |
| FR-02 | VAD / PTT bounds | MISSING | web + voice | FR-01 | Minimize audio sent | P0 | Voice fixtures |
| FR-03 | Speech-to-text | MISSING | `packages/voice` | STT adapter | Keys server-side | P0 | Mock + sample audio |
| FR-04 | Text input | MISSING | `apps/web`, `apps/api` | Sessions API | Input size limits | P0 | E2E text path |
| FR-05 | Streaming response | MISSING | api + web | Orchestrator | Cancel on barge-in | P1 | Integration stream |
| FR-06 | Text-to-speech | MISSING | `packages/voice` | TTS adapter | Keys server-side | P0 | Cancel + playback tests |
| FR-07 | Barge-in | MISSING | web + api + voice | FR-06, cancel tokens | Stop generation | P0 | Interrupt E2E |
| FR-08 | Multi-turn context | MISSING | conversation manager | DB | Bounded TTL | P0 | Unit context window |
| FR-09 | Intent routing | MISSING | orchestrator | Policy | No tool grant via intent spoof | P0 | Unit router |
| FR-10 | Cyber Florida RAG | MISSING | knowledge + worker | Ingest + embeddings | Untrusted retrieval | P0 | RAG evals |
| FR-11 | Source attribution | MISSING | api + web | FR-10 | XSS-safe source UI | P0 | Citation tests |
| FR-12 | Freshness | MISSING | ingest jobs | FR-10 | Stale events | P1 | Freshness eval cases |
| FR-13 | Program discovery | MISSING | RAG + tools | Approved sources | No invented eligibility | P1 | Knowledge eval |
| FR-14 | Cyber education | MISSING | orchestrator | Policy | Defensive only | P0 | Safety + quality |
| FR-15 | Incident guidance | MISSING | policy + orchestrator | Escalation matrix | No offensive steps | P0 | Safety evals |
| FR-16 | Scam analysis | MISSING | orchestrator | Size limits | No password collection | P0 | Safety evals |
| FR-17 | Approved navigation | MISSING | `packages/tools` | Domain allowlist | SSRF / open URL | P1 | Tool schema tests |
| FR-18 | Tool confirmation | MISSING | tools + UI | FR-17 | Side-effect gate | P1 | Policy tests |
| FR-19 | Error recovery | MISSING | all layers | Timeouts | Fail closed | P0 | Failure injection |
| FR-20 | Feedback | MISSING | api + web | Authz for review | No secrets in comments | P2 | API tests |
| FR-21 | Admin ingestion | MISSING | worker + admin | SSO/fail-closed | Privileged | P1 | Authz tests |
| FR-22 | Content lifecycle | MISSING | knowledge tables | Hashes | Poisoned corpus | P1 | Ingest tests |
| FR-23 | Analytics | MISSING | observability | Correlation IDs | No raw audio logs | P2 | Metric contract tests |
| FR-24 | Clear session | MISSING | api + web | Session token | Data deletion | P0 | API tests |
| FR-25 | Accessibility | MISSING | web | FR-04, FR-30 | — | P0 | Keyboard/a11y |
| FR-26 | Assistant states | MISSING | web | State machine | Truthful mic state | P0 | Unit transitions |
| FR-27 | Grounded generation | MISSING | orchestrator | FR-10 | Hallucination | P0 | RAG evals |
| FR-28 | AI disclosure | MISSING | policies + UI | — | Impersonation | P0 | Policy tests |
| FR-29 | Responsive UI | MISSING | web | — | — | P1 | Viewport E2E |
| FR-30 | Transcript | MISSING | web | FR-03/04 | XSS | P0 | A11y + unit |

---

## 3. Non-functional, security, privacy

| ID | Status | Notes |
|---|---|---|
| NFR-01–NFR-12 | MISSING | No runtime to measure |
| SEC-01–SEC-15 | MISSING | Controls specified in `docs/security/`; not in code |
| PRIV-01–PRIV-07 | MISSING | Retention policy documented in `docs/product.md`; not enforced |

Hardcoded credentials: **none found** (no env files, no source).

---

## 4. Specification items explicitly deferred

| Item | Status |
|---|---|
| Smart-home / device control | DEFERRED BY SPECIFICATION |
| Unrestricted web browsing | DEFERRED BY SPECIFICATION |
| Autonomous high-impact security actions | DEFERRED BY SPECIFICATION |
| Internal Cyber Florida systems access | DEFERRED BY SPECIFICATION |
| Long-term personal memory | DEFERRED BY SPECIFICATION |
| Mobile-native apps, kiosk, multilingual production | DEFERRED BY SPECIFICATION |
| User profiles / personalization | DEFERRED BY SPECIFICATION (Release 2+) |
| WebRTC SFU, Redis, dedicated vector DB, Kubernetes | DEFERRED BY SPECIFICATION until measured need |
| Multimodal screenshot/document analysis | DEFERRED BY SPECIFICATION (Release 2) |

---

## 5. Documentation vs implementation

| Artifact | Status |
|---|---|
| Project guide PDF | COMPLETE (spec only) |
| `docs/product.md` | COMPLETE for discovery (this phase) |
| `docs/policies.md` | COMPLETE as behavior spec; not loaded by code |
| `docs/architecture.md` | PARTIAL — target architecture written; **implemented architecture is empty** |
| `docs/REQUIREMENTS.md` | COMPLETE as requirements catalog |
| `docs/security/` | PARTIAL — planned controls, no runtime |
| `docs/decisions/` | COMPLETE for initial ADRs |
| `docs/runbooks/` | PARTIAL — templates; not operational |
| `docs/testing/` | PARTIAL — strategy; no tests |
| `docs/evaluations/` | PARTIAL — placeholders; no datasets scored |
| CI, Docker, app code | MISSING |

---

## 6. Duplicate systems / dead code / technical debt in software

None. There is no software to duplicate or delete.

Planning-doc overlap exists (`REQUIREMENTS.md` vs `product.md`, `SECURITY.md` vs `docs/security/`). That is documentation cross-reference, not competing runtimes. Canonical behavior is `docs/policies.md`. Canonical product scope is `docs/product.md`. Canonical target architecture is `docs/architecture.md`.

---

## 7. Highest-priority implementation order (after Phase 0)

Do not invert this order:

1. Engineering foundation (monorepo, CI, Compose, health)  
2. Accessible UI + mock conversation + text path  
3. Real voice loop with barge-in  
4. Orchestrator + policy loading  
5. RAG  
6. Tools  
7. Hardening, evals, observability, admin  

---

## 8. Conclusion

**Every runtime requirement is MISSING.** Phase 0 exit is documentation of scope and constraints, not a working assistant. No requirement is COMPLETE in software. Nothing is BROKEN because nothing runs. Claims of Pixel “listening,” “answering,” or “speaking” would be false.
