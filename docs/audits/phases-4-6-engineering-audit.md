# PIXEL ENGINEERING AUDIT

AUDIT RANGE:  
Phases 4–6

DATE:  
2026-08-14

BRANCH:  
`main`

COMMIT:  
`f2002df28ab59259f6f5ec44766f03f0977aec04`  
(`feat: implement Phases 2-6 from foundation through Cyber Florida RAG`)

WORKING TREE AT AUDIT START:  
Clean (`main` matched `origin/main`).

WORKING TREE AFTER AUDIT FIXES:  
Uncommitted audit fixes listed under FILES MODIFIED.

AUTHORITATIVE SPEC:  
`Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` — **not present in this workspace** (same gap as the Phases 0–3 audit). This audit used `docs/product.md`, `docs/ARCHITECTURE.md`, `docs/policies.md`, `docs/safety-rules.md`, `docs/escalation-matrix.md`, `docs/tool-confirmation-policy.md`, ADRs 0008–0011, Phase 4–6 completion notes, and the running code.

PHASE 7:  
Not started. No tools/actions/program-navigation features were added.

---

## PRE-AUDIT SNAPSHOT

```text
PIXEL PHASES 4–6 AUDIT PLAN

AUDIT RANGE: Phases 4–6 only (voice loop, orchestrator, Cyber Florida RAG)

CURRENT BRANCH: main

CURRENT COMMIT: f2002df28ab59259f6f5ec44766f03f0977aec04

WORKING TREE STATUS (start): clean, in sync with origin/main

PHASE 4 AREAS TO VERIFY:
  microphone, PTT capture, STT adapters, TTS adapters, playback queue,
  barge-in, stale turns, latency metrics, credential isolation

PHASE 5 AREAS TO VERIFY:
  process_turn boundary, session bounds/clear, intent router, policy 1.3.0,
  timeouts/retries/cancellation, output validation, text/voice unification

PHASE 6 AREAS TO VERIFY:
  allowlist, HTML ingest/chunk/embed, retrieval, grounding, citations,
  abstention, freshness, inactive sources, retrieved injection, eval metrics

TESTS TO RUN:
  ruff format/check, pyright, pytest, prettier, eslint, tsc, vitest,
  next build, Playwright e2e, pip-audit, npm audit, knowledge evaluate()

RUNTIME TESTS TO RUN:
  Playwright Chromium with fake microphone; API /health via e2e webServer;
  in-process mock voice/text latency measurement

SECURITY TESTS TO RUN:
  prompt-injection e2e + unit; retrieved-injection unit; CORS; admin fail-closed;
  NEXT_PUBLIC secret-shaped env rejection; pip-audit; npm audit --audit-level=high

RAG EVALUATIONS TO RUN:
  python evaluate(load_cases(evals/knowledge/cases.jsonl)) against fixture_retriever

VOICE TESTS TO RUN:
  Playwright PTT + barge-in; pytest STT/TTS adapters; playback queue unit tests

DATABASE / MIGRATION TESTS TO RUN:
  packages/pixel/tests/test_knowledge_postgres.py (requires PIXEL_TEST_DATABASE_URL)

KNOWN RISKS:
  PDF spec missing; default local providers are mock; no OPENAI_API_KEY;
  KNOWLEDGE_STORE unused by VoiceRuntime; postgres tests skip without Docker;
  live speech recognition not verifiable in this environment
```

========================================

## EXECUTIVE SUMMARY

OVERALL RESULT:  
PARTIAL

OVERALL SCORE:  
84/100

READY FOR PHASE 7:  
YES

Phases 4–6 are implemented as a connected system: push-to-talk voice and text enter one orchestrator, organization facts require retrieval from an allowlisted fixture index, citations attach from retrieved chunks, and missing evidence abstains. Required format, lint, typecheck, unit, e2e, build, and dependency scans passed after the audit fix.

This is **not** a verified live-vendor production assistant. Default local STT/LLM/TTS/embeddings are mock. There is no `.env` and no `OPENAI_API_KEY` in this workspace. PostgreSQL/pgvector exists as schema + store code but is **not** what the API process queries. Live speech recognition, live embeddings, and a fresh database migrate were **NOT VERIFIED**.

One HIGH defect was found and fixed: the OpenAI LLM adapter dropped retrieved evidence, so a live model would have answered from memory while the orchestrator still attached citations. After that fix, remaining issues are MEDIUM/LOW or environment verification gaps.

========================================

## PHASE 4 — VOICE LOOP

STATUS:  
PARTIAL

SCORE:  
78/100

MICROPHONE:  
PASS (unit + Playwright fake device). `getUserMedia` permission granted/denied/unavailable; 5s timeout treats hang as unavailable; tracks stopped on `release()`. Audit fix: release any prior stream before a new `getUserMedia`. Real hardware disconnect and a physical mic were **NOT VERIFIED**. Capture uses `ScriptProcessor` (deprecated) into PCM16 at 16 kHz.

TURN DETECTION:  
PASS as **push-to-talk** (ADR-0003). Not VAD. Short captures under ~180 ms return to idle without a turn. Silence in STT raises `empty`. Pixel is not left waiting on VAD silence because the user must press Stop.

STT:  
PARTIAL. Interface `SpeechToTextProvider` with `mock` and `openai` adapters. Mock STT does **not** decode speech; non-silent audio yields the fixture transcript `What is Cyber Florida?`. OpenAI Whisper adapter is contract-tested (normalization, auth header) against `httpx.MockTransport`. Live Whisper: **NOT VERIFIED** (no API key). Empty transcript and cancellation are handled in `run_voice_turn`.

TTS:  
PARTIAL. Mock TTS emits a generated WAV (measured 13484 bytes on a sample turn), not a prerecorded product clip. OpenAI `tts-1` adapter is contract-tested. Live vendor TTS: **NOT VERIFIED**. TTS failure keeps text (`tts_failure` warning path).

AUDIO PLAYBACK:  
PASS (unit). Single queue (`createQueuePlayback`) over `decodeAudioData`. `stop()` increments a generation token so late decode cannot play. No object URLs. Overlapping play is prevented by stop-before-start. `AudioContext` is not closed for the page lifetime (LOW leak).

BARGE-IN:  
PASS on the connected mock path. Starting listen while `speaking` or `processing` calls `abortActive`: playback `stop()`, realtime cancel, capture stop, abort controller. Playwright: speaking/processing → Interrupt → listening. This is not UI-only; `playback.stop()` is invoked. Live overlapping human speech against live TTS: **NOT VERIFIED**.

REPEATED INTERRUPTION:  
PARTIAL. Unit tests cover stale playback after stop. Playwright covers one barge-in, not interrupt → new response → interrupt again in one scenario. No evidence of overlapping queues in code.

STALE TURN PROTECTION:  
PASS. Client ignores results unless `activeTurnId` matches. Session `commit_turn` requires matching `generation` and `turn_id`. Cancelled WS turns are dropped. Late Turn A cannot commit over Turn B.

LATENCY INSTRUMENTATION:  
PASS for metrics the architecture actually has. Measured on the mock path (in-process, this audit):

| Metric | Voice sample | Text sample |
|---|---|---|
| time_to_transcript_ms | 2 | n/a (text) |
| model_latency_ms | 0 | 0 |
| tts_latency_ms | 4 | 6 |
| time_to_first_audio_ms | 15 | 50 |
| total_turn_latency_ms | 15 | 50 |
| retrieval_latency_ms | 12 | 9 |

Not implemented (not faked): `end_of_turn_latency` (no VAD), `backend_latency` as a separate span, `time_to_first_token` (non-streaming LLM), `barge_in_cancellation_latency`. These mock numbers are **not** live OpenAI latency.

VOICE FAILURE HANDLING:  
PASS for mapped cases: mic denied/unavailable (unit), silence/empty (orchestrator), STT/model/TTS/network (API + e2e `simulate network error`), text fallback remains available while voice is in an error state.

SECURITY:  
PASS for Phase 4 scope. No OpenAI SDK in frontend. `OPENAI_API_KEY` is server-only. `NEXT_PUBLIC_*` names containing `API_KEY`/`SECRET`/`TOKEN`/`PASSWORD`/`PRIVATE` throw. `.env` gitignored; no `.env` present; example keys empty. Errors do not include `sk-`. Logs use session/turn/intent/status, not transcripts or audio.

EXIT CRITERIA:

```text
MULTIPLE CONSECUTIVE VOICE TURNS WORK     PASS (Playwright sequential tests, one worker)
BARGE-IN WORKS RELIABLY                   PASS (code + Playwright; live dual-talk NOT VERIFIED)
PROVIDER CREDENTIALS ARE SECURE           PASS
REAL VOICE PATH IS CONNECTED              PARTIAL (adapters wired; default STT is mock fixture)
```

ISSUES:

- Live vendor STT/TTS not run. Mock STT always returns the same Cyber Florida question, so consecutive “voice” turns are not distinct utterances.
- `barge_in_cancellation_latency` is not recorded.
- Deprecated `ScriptProcessor` capture.
- OpenAI HTTP STT/TTS/LLM does not abort the in-flight request on cancel; the orchestrator discards the result after return.

FIXES:

- Microphone: release existing `MediaStream` before a new `getUserMedia`.
- `docs/voice.md`: document `retrieval_latency_ms`.

========================================

## PHASE 5 — ORCHESTRATOR

STATUS:  
PASS WITH MINOR ISSUES

SCORE:  
91/100

CENTRAL ORCHESTRATOR:  
PASS. `pixel.orchestrator.process.process_turn` is the only intelligence boundary. `run_text_turn` and `run_voice_turn` both call it after STT. API `POST /v1/turns` and `WS /v1/realtime` call those helpers, not the LLM.

DIRECT AI CALLS OUTSIDE BOUNDARY:  
0 in application code. `LLMProvider.generate` is used from the orchestrator, provider adapters, and tests. No OpenAI imports in `apps/web`. Frontend `mock-provider.ts` is **test-only** (`use-conversation.test.ts`); production UI uses `createHttpTurnClient`.

SESSION MANAGEMENT:  
PASS. In-memory `SessionStore`, UUID ids, TTL 1800s, max 500 sessions, prune on create. Unknown/expired sessions error closed. `get_or_create` does not silently invent a missing id when one is supplied (`get` raises).

BOUNDED CONTEXT:  
PASS on the server: `MAX_MESSAGES = 8` (sliding). No long-term memory. Frontend display cap `MAX_TURNS = 40` is UI-only and can show more turns than the model sees (MEDIUM mismatch).

CLEAR SESSION:  
PASS. `POST /v1/sessions/{id}/clear` increments generation, cancels active turn, wipes messages. Playwright: after clear, “What about that?” does not reuse prior program context.

INTENT ROUTING:  
PASS. Deterministic six-way router (`cyberflorida_knowledge`, `cybersecurity_help`, `scam_help`, `navigation`, `clarification`, `unsupported`). Not a mocked classifier output. Follow-ups use `last_intent`. Injection-shaped input routes to unsupported/refusal. Ambiguous empty text → clarification, skip model.

POLICY LOADING:  
PASS. Server-only `packages/pixel/pixel/orchestrator/policy.py`: `pixel-behavior` **1.3.0**. Users cannot POST a system prompt. Frontend has no privileged policy. Phase 5 completion report still says 1.2.0 (docs drift).

POLICY VERSIONING:  
PASS. Version returned on responses; stored on session.

TIMEOUTS:  
PASS. httpx timeouts: STT 20s, LLM 25s, TTS 20s, source fetch 20s. Settings-configurable. No unbounded client found on provider calls.

RETRIES:  
PASS. Max 2 attempts, exponential backoff, only `ProviderError.retryable` (timeout, 429, transport). Auth/invalid/cancel not retried. Cancellation checked before each attempt.

CANCELLATION:  
PASS. `CancellationFlag` on session active turn; WS cancel; HTTP abort on the client. In-flight OpenAI POST is not aborted (MEDIUM).

OUTPUT VALIDATION:  
PASS. Empty/overlong/secret-or-policy-leak patterns → safe fallback. Invalid structured extras are not executed (tools are Phase 7 and `executed=False`).

SAFE FALLBACK:  
PASS. Provider errors map to user-facing copy via `user_facing`; e2e network simulation shows a connection problem, not a stack trace or API key.

TEXT / VOICE UNIFICATION:  
PASS. Both become text then `process_turn`. No second intelligence path in the API. (Legacy frontend mock provider is unused in production UI.)

EXIT CRITERIA:

```text
ALL AI REQUESTS FLOW THROUGH CONTROLLED ORCHESTRATOR   PASS
CONVERSATION STATE IS BOUNDED                          PASS
CONVERSATION STATE IS TESTABLE                         PASS
POLICY VERSIONING EXISTS                               PASS (1.3.0)
SAFE FALLBACKS WORK                                    PASS
CANCELLATION WORKS                                     PASS
```

ISSUES:

- Frontend transcript list (40) vs backend history (8).
- Phase 5 completion report lists policy 1.2.0.
- OpenAI generate is non-streaming; `time_to_first_token` is not a real span.

FIXES:

- OpenAI adapter now appends retrieved evidence to the system message, labeled untrusted DATA (this is also a Phase 6 grounding fix). Contract test added.

========================================

## PHASE 6 — RAG

STATUS:  
PARTIAL

SCORE:  
83/100

SOURCE REGISTRY:  
PASS. `packages/pixel/pixel/knowledge/registry.py`: explicit IDs, titles, canonical HTTPS `cyberflorida.org` URLs, access class `public`, topic/audience, fixture keys. `require_approved_url` rejects other hosts. User URLs cannot become authoritative knowledge.

SOURCE CONTROLS:  
PASS for public-only current inventory. No internal corpus is registered. A test injects an `internal` chunk and verifies public search cannot return it. Admin ingest routes fail closed (`ADMIN_ENABLED=false` → 403).

INGESTION:  
PASS for **HTML** (stdlib parser). Empty/nav-only HTML is a parse failure. Failed ingest keeps the last good version (tested). PDF/DOCX: **not implemented** and not claimed as required by ADR-0011 while the inventory is HTML-only.

NORMALIZATION:  
PASS. NFKC, heading preservation, boilerplate nav dropped, facts not rewritten (extract + normalize, not an LLM rewrite).

CHUNKING:  
PASS. Heading-first sections with 1200-character secondary split. Stable sha256 chunk IDs. Not naïve “every 500 characters”.

EMBEDDINGS:  
PARTIAL. `HashEmbeddingProvider` (1536-d) used by the live API retriever. `OpenAIEmbeddingProvider` exists and is contract-tested. `EMBEDDING_PROVIDER` on Settings is **not** read by `VoiceRuntime`. Live OpenAI embeddings: **NOT VERIFIED**.

VECTOR STORAGE:  
PARTIAL. `001_knowledge.up.sql` + `CREATE EXTENSION vector`, FKs, metadata indexes. No ivfflat/hnsw index. `PostgresKnowledgeStore` implemented. **API always uses `fixture_retriever()` in-memory cosine index.** `KNOWLEDGE_STORE=postgres` does not change runtime behavior.

RETRIEVAL:  
PASS on the fixture index. Relevant: FirstLine query ranks `cf-firstline`. Unrelated pasta query → no acceptable hits. `top_k` default 5, `min_score` 0.08, both settings-configurable and applied on the fixture retriever. No reranker (ADR-0011; acceptable).

METADATA FILTERING:  
PASS in store implementations (`active`, `access_class`). Inactive FirstLine chunks are not returned (in-memory test). Postgres equivalent skipped without `PIXEL_TEST_DATABASE_URL`.

GROUNDING:  
PASS on the mock-LLM + fixture path: org intent sets `requires_retrieval=True`; no hits → canned `ORG_ABSTAIN` and the model is skipped. With hits, evidence is passed to the LLM request. **Before this audit, OpenAI `generate` ignored `request.evidence` (HIGH, fixed).** Eval groundedness 100% is measured against MockLLM extracting evidence text, not a live chat model.

ABSTENTION:  
PASS. Missing evidence and unavailable retriever abstain. Eval abstention 92.3% on 13 cases. Playwright clear-conversation follow-up asks for clarification rather than inventing “that one”.

FRESHNESS:  
PARTIAL. Pixel answers from the **indexed fixture snapshot**, not a live crawl at query time. Freshness eval 93.3% means the fixture/eval pair agrees, not that cyberflorida.org was fetched today. Live refresh of production pages: **NOT VERIFIED**. If evidence is missing, it abstains rather than guessing dates/leadership.

SOURCE TRACEABILITY:  
PASS. Chunks carry `chunk_id`, `document` fields, `source_id`, canonical URL. Citations `provenance="retrieval"`. No anonymous evidence in the retriever result type.

CITATIONS:  
PASS as retrieval-linked SourceRef/Citation, not decorative UI URLs. E2E “What is Cyber Florida?” shows an approved source card with the grounded answer. Eval citation correctness 88.9%. Citation correctness is “expected source URL present,” not claim-by-claim NLI.

REFRESH:  
PASS in unit tests: unchanged content hash → no re-embed; changed HTML → new index; failed empty parse → previous version kept.

DEACTIVATION:  
PASS in-memory. Postgres deactivate **NOT VERIFIED** (skipped test).

PROMPT-INJECTION DEFENSE:  
PASS. Retrieved injection fixture cannot dump policy, grant admin tools, or reveal keys (unit). Evidence delimiters + policy + MockLLM strips injection-shaped retrieved text. User injection e2e refused.

RAG EVALUATION:  
PASS dataset exists (`evals/knowledge/cases.jsonl`, 122 cases) covering the required categories. Runner `pixel.knowledge.evaluate.evaluate` was executed in this audit (see RAG METRICS). Thresholds in pytest were not lowered.

EXIT CRITERIA (Phase 6 as implemented for local/CI):

```text
ALLOWLISTED SOURCES ONLY          PASS
RETRIEVAL IS REAL (not keyword)   PASS (cosine over hash embeddings)
ORG ANSWERS REQUIRE EVIDENCE      PASS
ABSTAIN WITHOUT EVIDENCE          PASS
CITATIONS FROM RETRIEVAL          PASS
INACTIVE SOURCES FILTERED         PASS (memory); postgres NOT VERIFIED
POSTGRES USED BY API              FAIL / unused (documented)
LIVE EMBEDDINGS                   NOT VERIFIED
```

ISSUES:

- API ignores `KNOWLEDGE_STORE` and `EMBEDDING_PROVIDER`.
- Postgres migration test skipped.
- No ANN vector index.
- Eval groundedness inflated by MockLLM.
- Context precision 47.7% (top_k=5 often includes extra sources).
- UI previously claimed “RAG is not implemented” (fixed).

FIXES:

- OpenAI evidence attachment + test.
- Document unused store/embedding settings in `docs/knowledge.md` and env examples.
- Hero banner now describes approved-source answers instead of “RAG is not implemented”.

========================================

## RAG METRICS

Measured 2026-08-14 against `evals/knowledge/cases.jsonl` and `fixture_retriever()` + `MockLLM`. Do not treat these as live-model scores.

TOTAL EVALUATION CASES:  
122 (109 retrieval cases, 13 abstention cases)

RETRIEVAL HIT RATE:  
Hit@1 75.2% · Hit@3 94.5% · Hit@5 95.4%

CONTEXT PRECISION:  
47.7%

GROUNDEDNESS:  
100% (MockLLM extracts retrieved text; live model **NOT VERIFIED**)

ANSWER CORRECTNESS:  
77.1%

CITATION CORRECTNESS:  
88.9%

ABSTENTION QUALITY:  
92.3% (13 cases)

FRESHNESS:  
93.3%

Retrieval latency (eval loop): p50 12 ms · p95 18 ms

========================================

## VOICE METRICS

Mock path, in-process sample during this audit (not OpenAI, not a browser).

TIME TO TRANSCRIPT:  
2 ms (voice sample)

TIME TO FIRST AUDIO:  
15 ms (voice) · 50 ms (text+TTS)

TOTAL TURN LATENCY:  
15 ms (voice sample) · 50 ms (text sample)

BARGE-IN CANCELLATION:  
**NOT INSTRUMENTED.** Playwright confirms state + `playback.stop()`; no millisecond metric.

========================================

## ISSUES FOUND

CRITICAL:  
- None.

HIGH:  
- OpenAI LLM adapter omitted `LlmRequest.evidence`, so a live model would answer without retrieved documents while citations could still be attached. **Fixed in this audit.**
- Live vendor STT/TTS/LLM/embeddings were not run (no key). This is a **verification gap**, not a missing adapter. It is scored in Phase 4/6 PARTIAL status rather than left as an open HIGH code defect. Do not claim production speech recognition works.

MEDIUM:  
- `VoiceRuntime` always uses `fixture_retriever()`; `KNOWLEDGE_STORE` / `EMBEDDING_PROVIDER` unused.
- Postgres/pgvector migrate+search skipped (`PIXEL_TEST_DATABASE_URL` unset).
- Knowledge SQL has no ivfflat/hnsw index.
- Frontend `MAX_TURNS=40` vs backend `MAX_MESSAGES=8`.
- No `barge_in_cancellation_latency` (or VAD end-of-turn) instrumentation.
- Deprecated ScriptProcessor capture; playback AudioContext never closed.
- OpenAI HTTP calls are not aborted mid-request on cancel.
- RAG eval groundedness uses MockLLM + token overlap, so 100% overstates live grounding.
- Context precision 47.7%.
- PDF/DOCX parsers absent (acceptable under ADR-0011; still a format gap vs the audit checklist).
- Authoritative PDF spec file missing from the repo.
- Phase 5 completion report still lists policy 1.2.0.
- Playwright barge-in does not cover interrupt → new audio → interrupt again.
- Sessions remain in-memory (ADR-0005 deferred; not Phase 7).

LOW:  
- `type: ignore` on SQL execute and orchestrator status/safety literals.
- Starlette `TestClient` deprecation warning.
- Windows WebSocket `ConnectionResetError` on Playwright teardown (tests still passed).
- Frontend `mock-provider.ts` remains for tests (not on the production path).

========================================

## ISSUES FIXED:

- Attached untrusted retrieved evidence to OpenAI chat completions; added contract test.
- Release prior microphone stream before a new `getUserMedia`.
- Corrected UI banner that said RAG was not implemented.
- Documented fixture-index runtime vs `KNOWLEDGE_STORE` in knowledge docs and env examples.
- Documented `retrieval_latency_ms` in voice docs.

========================================

## FILES MODIFIED:

- `packages/pixel/pixel/providers/openai.py`
- `packages/pixel/tests/test_openai_adapters.py`
- `apps/web/src/conversation/microphone.ts`
- `apps/web/src/components/PixelAssistant.tsx`
- `docs/knowledge.md`
- `docs/voice.md`
- `.env.example`
- `.env.production.example`
- `.env.staging.example`
- `docs/audits/phases-4-6-engineering-audit.md` (this file)

========================================

## TESTS RUN

COMMAND:  
`python -m ruff format --check apps/api apps/worker packages/pixel`  
RESULT:  
PASS (after test-file format fix)

COMMAND:  
`python -m ruff check apps/api apps/worker packages/pixel`  
RESULT:  
PASS

COMMAND:  
`python -m pyright`  
RESULT:  
PASS (0 errors)

COMMAND:  
`python -m pytest`  
RESULT:  
PASS — 88 passed, 1 skipped (`PIXEL_TEST_DATABASE_URL is not set`)

COMMAND:  
`python -c "from pixel.knowledge.evaluate import default_cases_path, evaluate, load_cases; print(evaluate(load_cases(default_cases_path())))"`  
RESULT:  
PASS — metrics recorded above

COMMAND:  
`npm run web:format:check`  
RESULT:  
PASS

COMMAND:  
`npm run web:lint`  
RESULT:  
PASS

COMMAND:  
`npm run web:typecheck`  
RESULT:  
PASS

COMMAND:  
`npm run web:test`  
RESULT:  
PASS — 37 tests, 9 files

COMMAND:  
`npm run web:build`  
RESULT:  
PASS — Next.js 16.3.1

COMMAND:  
`npm run web:e2e`  
RESULT:  
PASS — 7 Playwright Chromium tests (text+source, network fallback, voice PTT, barge-in, follow-up, clear, injection)

COMMAND:  
`python -m pip_audit`  
RESULT:  
PASS — no known vulnerabilities (local package `pixel` skipped as not on PyPI)

COMMAND:  
`npm audit --audit-level=high`  
RESULT:  
PASS — 0 vulnerabilities

COMMAND:  
In-process mock voice/text `process_turn` / `run_voice_turn` latency sample  
RESULT:  
PASS — timings recorded above; mock TTS returned WAV bytes

COMMAND:  
Postgres `upgrade` / `downgrade` against a live database  
RESULT:  
NOT VERIFIED — skipped test, no `PIXEL_TEST_DATABASE_URL`

COMMAND:  
Live OpenAI Whisper / chat / TTS / embeddings  
RESULT:  
NOT VERIFIED — `ENV_FILE=absent`, `openai_key_configured=False`

COMMAND:  
Physical microphone / dual-talk barge-in  
RESULT:  
NOT VERIFIED — Playwright fake media device only

========================================

## TEST RESULTS

PASSED:  
ruff format, ruff check, pyright, pytest 88, prettier, eslint, tsc, vitest 37, next build, Playwright 7, pip-audit, npm audit, knowledge evaluate() 122 cases, API health via e2e webServer

FAILED:  
0 (after the OpenAI adapter test was restored/formatted)

SKIPPED:  
1 — `test_postgres_upgrade_downgrade_and_search`

NOT VERIFIED:  
Live OpenAI providers; real microphone hardware; VAD; postgres migrations; live cyberflorida.org fetch; barge-in cancellation latency; PDF spec file; interrupt-again voice scenario; claim-level citation NLI

========================================

## SECURITY FINDINGS:

- No live provider secrets in the repo or committed `.env`.
- CORS is an explicit origin allowlist; `*` rejected by Settings.
- Admin source APIs fail closed.
- Prompt injection (user) refused in e2e; retrieved injection remains data in unit tests.
- OpenAI evidence omission would have been a grounding/security-adjacent failure in production LLM mode; fixed.
- Full Phase 8 hardening is still ahead (auth, rate limits, persistent session abuse).

========================================

## PRIVACY FINDINGS:

- Raw audio is bounded in memory (`MAX_AUDIO_BYTES = 1_000_000`) and not written to disk in the inspected path.
- Sessions are in-memory with TTL and user clear; not long-term personal memory.
- Logs inspected: correlation/session/turn/intent/status/source ids — not full transcripts, not WAV, not API keys.
- Retention days remain UNASSIGNED in product policy (documented). Mock STT does not persist utterances.

========================================

## ARCHITECTURE FINDINGS:

- Voice and text unify in `process_turn`. Provider SDKs stay in `packages/pixel/pixel/providers` and `knowledge/embeddings.py`.
- PTT over WebSocket matches ADR-0003.
- RAG matches ADR-0011 for local/CI (fixture index). Production-shaped env vars over-promise postgres/OpenAI embeddings relative to `VoiceRuntime`.
- Tools remain explicitly unimplemented (`ToolDecision.executed=False`, reason Phase 7).
- Domain models (`SourceRef`, `Citation`, `Turn`, `Message`, `AssistantResponse`) exist on the backend; frontend `SourceRef` matches the public JSON shape.

========================================

## FALSE COMPLETION FINDINGS:

- Hero copy said “RAG is not implemented” after Phase 6 shipped (fixed).
- `.env.production.example` set `KNOWLEDGE_STORE=postgres` without the API reading it (commented; still unused).
- A previous agent could have claimed live OpenAI RAG grounding; the OpenAI adapter did not send evidence until this audit.
- Phase 5 completion report lists policy 1.2.0; code is 1.3.0.
- Phase 4/6 completion reports already marked live vendor / postgres as unverified; those claims were not treated as proof.

========================================

## PLACEHOLDER / MOCK FINDINGS:

- Default `LLM_PROVIDER`/`STT_PROVIDER`/`TTS_PROVIDER`/`EMBEDDING_PROVIDER=mock` for `PIXEL_ENV=local` (ADR-0007; production Settings reject mock).
- Mock STT fixture transcript is a test double, not recognition.
- `apps/web/src/conversation/mock-provider.ts` is unused by `PixelAssistant` (tests only).
- Hash embeddings are a deterministic stand-in for vendor embeddings.
- No TODO/FIXME/HACK/NOT IMPLEMENTED in application Python/TS for required Phase 4–6 features. Tool reason string “Phase 7 tools are not implemented” is accurate and out of this audit’s build scope.

========================================

## REMAINING TECHNICAL DEBT:

- Wire `VoiceRuntime` to postgres + configured embedder when explicitly enabled, with fail-closed empty-index behavior.
- Add pgvector ANN index when postgres is the live store.
- Instrument barge-in cancel latency.
- Replace ScriptProcessor with AudioWorklet (a `capture-worklet.js` already exists in `public/`).
- Align UI history cap with server `MAX_MESSAGES`.
- Abort or time-bound in-flight OpenAI requests on cancel.
- Re-run RAG eval with a live LLM before treating groundedness 100% as operationally true.

========================================

## DEFERRED ISSUES:

- Phase 7 tools, confirmation, and program navigation (explicitly out of scope).
- Phase 8 auth, rate limits, hardened admin ingest.
- Persistent postgres sessions (ADR-0005).
- VAD (PTT is the approved first mechanism).
- PDF/DOCX until an approved non-HTML source is registered.
- Live vendor verification until an operator supplies `OPENAI_API_KEY` locally.
- Numeric retention TTL days (UNASSIGNED owners).

========================================

## REGRESSION RISKS:

- Switching `LLM_PROVIDER=openai` without this evidence fix would have produced ungrounded org answers; that path is now attached. Still untested live.
- Enabling `KNOWLEDGE_STORE=postgres` today changes **nothing** at runtime; operators may think they left fixtures.
- Mock STT always asking “What is Cyber Florida?” can hide follow-up/barge-in bugs that only appear with distinct utterances.
- Frontend still contains a Phase 3 mock provider; a future wiring mistake could bypass the API.

========================================

## FINAL VERDICT

PHASE 4:  
PARTIAL

PHASE 5:  
PASS

PHASE 6:  
PARTIAL

OVERALL:  
PARTIAL

READY FOR PHASE 7:  
YES

REASON:  
The orchestrator, bounded sessions, policy, text/voice unification, fixture RAG, citations, abstention, and barge-in-on-the-connected-mock-path are sound enough to add tools behind the existing `ToolDecision` hook. Live speech vendors and postgres retrieval remain unverified and must not be described as production-complete. No remaining CRITICAL/HIGH code defects after the OpenAI evidence fix. Required builds and tests passed.

NEXT RECOMMENDED ACTION:  
Wait for explicit instruction: `Proceed to Phase 7.` Optionally, before tools: set `OPENAI_API_KEY` and verify live STT/TTS/LLM grounding, and/or set `PIXEL_TEST_DATABASE_URL` and run postgres migrations. Do not start Phase 7 until that instruction.
