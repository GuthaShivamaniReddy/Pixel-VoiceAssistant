# Pixel — Repository Assessment

**Document status:** Phase 0 (Architecture / Planning)  
**Assessed:** 2026-08-14  
**Workspace:** `PIXEl VA`  
**Source of product intent:** `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` (v1.0, August 2026)

This assessment records what exists in the workspace **before** any application code is written. Nothing in this document should be read as implemented software.

---

## 1. Summary

The repository is a **greenfield workspace**. It is not an application yet.

| Question | Finding |
|---|---|
| Is the repository empty of software? | **Yes.** No application source, tests, configs, or infrastructure. |
| Is it a git repository? | **No.** No `.git` directory. |
| Is there a working product? | **No.** |
| What exists? | One project-guide PDF. |

**Current status:** Architecture / Planning only. Pixel cannot listen, reason, retrieve, or speak.

---

## 2. What exists

### 2.1 Files found

| Path | Type | Role |
|---|---|---|
| `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` | PDF, 27 pages | Product description, requirements, architecture guidance, 14-phase development method, testing, operations, risks, and definition of done. |

No other files, directories, or hidden project metadata were present at inspection (no `package.json`, `pyproject.toml`, `Dockerfile`, `.env`, CI configs, or source trees).

Phase 0 documentation in `docs/` (including `product.md`, `policies.md`, `architecture.md`) is produced **after** inspection. Those files are planning artifacts, not runtime software.

### 2.2 Frameworks, languages, and runtimes

| Area | Status |
|---|---|
| Frontend | None |
| Backend | None |
| APIs | None |
| Database | None |
| Testing | None |
| Environment configuration | None |
| AI integrations | None |
| Voice integrations | None |
| Deployment configuration | None |
| CI/CD | None |
| Documentation (pre-Phase 0) | PDF guide only |

### 2.3 What the PDF provides (reusable as design input)

The PDF is **not code**. It is reusable as a blueprint:

- Product identity: Pixel as Cyber Florida’s voice and conversational interface.
- User groups, use cases, MVP vs later releases, out-of-scope items.
- Functional / non-functional / security / privacy / UX requirements with IDs.
- Logical architecture, service boundaries, suggested monorepo layout.
- Provider-abstraction intent (do not lock core logic to one vendor).
- Recommended stack hints: React/Next.js client, FastAPI backend, PostgreSQL + pgvector, containerization.
- Voice loop, RAG, tools, security, observability, and operations guidance.
- Phased build order and production definition of done.

These recommendations are **design guidance**. They must still be validated against Cyber Florida / USF technology, security, procurement, accessibility, and privacy requirements before production adoption.

---

## 3. What is reusable

| Asset | Reuse decision |
|---|---|
| Project-guide PDF | **Reuse as requirements and architecture source.** Do not treat it as implemented behavior. |
| Existing application code | **None.** |
| Existing tests | **None.** |
| Existing CI | **None.** |
| Existing secrets / env files | **None found** (good: nothing to rotate or leak). |
| Vendor SDKs / API keys | **None found.** |

There is **no working code to duplicate or preserve**. Phase 1+ must create the first systems rather than wrap existing ones.

---

## 4. What is incomplete

Everything required for a production assistant is incomplete, including:

- Git history and contribution workflow.
- Monorepo / package layout.
- Frontend UI and assistant state machine.
- Backend API, conversation manager, orchestrator.
- Speech-to-text, text-to-speech, and voice transport.
- LLM, embeddings, vector store, RAG ingestion.
- Database schema and migrations.
- Tool registry and policy engine.
- Safety / policy layer and response validation.
- Authentication / authorization (including admin).
- Rate limiting, CORS, security headers.
- Observability (logs, metrics, traces, correlation IDs).
- Tests, linting, type checking, production build.
- Deployment, environments, secrets management, CI/CD.
- Knowledge corpus and evaluation sets.
- User-facing privacy / AI notices.

---

## 5. Potential architectural problems (if built naively)

These are **risks to avoid**, not defects in existing code:

1. **Vendor lock-in** — calling OpenAI/Anthropic/Deepgram SDKs directly from UI or orchestrator logic.
2. **Secrets in the browser** — putting long-lived STT/TTS/LLM keys in client bundles.
3. **RAG as trusted instruction** — letting retrieved web/PDF text override system policy or invoke tools.
4. **Monolithic “chat function”** — mixing transport, STT, retrieval, tools, and TTS in one module.
5. **Premature microservices** — splitting gateway / orchestrator / knowledge / tools before a vertical slice works.
6. **WebRTC-first complexity** — implementing full mesh audio before a simpler push-to-talk + WebSocket loop is proven.
7. **Unbounded conversation memory** — storing sensitive user content indefinitely.
8. **Admin without authz** — knowledge ingestion endpoints that exist before authentication is real.
9. **Hallucinated Cyber Florida facts** — answering org-specific questions from model memory instead of RAG.
10. **Demo-first UI** — animations and avatars before barge-in, captions, and error recovery work.

The architecture in `ARCHITECTURE.md` is designed to prevent these.

---

## 6. Technical debt

**Current technical debt: none in software** (there is no software).

Debt that will appear immediately if Phase 1 is skipped or rushed:

| Debt | How it appears | Prevention |
|---|---|---|
| Undocumented env contract | Hidden keys, broken onboarding | `.env.example` only; no real secrets in git |
| Mixed language styles | Inconsistent TS/Python layout | Lint, format, typecheck in CI from Phase 2 |
| Unversioned prompts | Irreproducible answers | Policy/prompt versioning from orchestrator phase |
| Unversioned knowledge index | Stale or unreproducible RAG | Ingestion jobs + content hashes |
| Tests that need live APIs | Flaky CI, secret leakage | Provider mocks/fixtures required |

---

## 7. Important risks

| Risk | Severity | Notes |
|---|---|---|
| Empty repo mistaken for a working app | High | README must state Architecture / Planning only. |
| Building UI or RAG before the voice loop | High | First vertical slice is microphone → STT → answer → TTS → barge-in. |
| Treating the PDF as source of truth for live Cyber Florida facts | High | Facts must come from an approved, ingested corpus later. |
| Prompt injection via retrieved pages | High | Retrieved content is untrusted data. See `SECURITY.md`. |
| Audio / transcript retention without policy | High | Default: transient audio; bounded conversation retention. |
| USF / Cyber Florida compliance not yet validated | High | Stack choices are engineering recommendations, not procurement approval. |
| No git / no CI | Medium | Foundation phase must add VCS, hooks-friendly CI, and secret scanning. |
| Workspace path contains spaces (`PIXEl VA`) | Low | Scripts and Docker mounts must quote paths. |

---

## 8. Recommended starting posture

1. Treat this workspace as **greenfield**.
2. Adopt the stack and boundaries in `ARCHITECTURE.md` (evaluated against an empty repo).
3. Do **not** invent a second architecture or a second voice/RAG stack later.
4. Do **not** begin Phase 1 until Phase 0 documents are accepted.
5. First implementation increment (later phases): engineering foundation, then identity/policy docs as code constraints, then a mocked UI, then a real voice loop.

---

## 9. Assessment conclusion

| Criterion | Result |
|---|---|
| Existing product to extend | No |
| Existing architecture to preserve | No (design only, in the PDF) |
| Duplicate systems present | No |
| Secrets present | No |
| Safe to design from scratch | **Yes** |
| Safe to claim any runtime capability | **No** |
