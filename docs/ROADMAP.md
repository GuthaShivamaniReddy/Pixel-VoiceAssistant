# Pixel — Roadmap

**Document status:** Specification Phase 0 (product discovery and constraints) is complete as documentation. **Do not start the next phase automatically.**

This roadmap follows the project-guide PDF’s fourteen-phase method. Pixel has **no application code**.

---

## Status

| Phase | Name | Status |
|---|---|---|
| 0 | Product discovery and constraints | **Complete (docs)** |
| 1 | Assistant identity, conversation policy, and safety rules | **Complete (docs)** — policy `1.1.0`; 102 examples |
| 2–14 | Foundation through continuous improvement | **Not started** |

No application code, tests, or production build exist.

---

## Phase 0 — Product discovery and constraints

**Objective:** Turn the idea into a precise product problem, scope, and measurable MVP **before code**.

**Documented in:** `docs/product.md`, `docs/GAP_ANALYSIS.md`, `docs/policies.md` (Phase 0 constraints only), `docs/risk-register.md`.

**Exit criteria (PDF):** Stakeholders agree on MVP; content owners identify authoritative sources; security/privacy constraints recorded.

| Exit item | State |
|---|---|
| Ownership named | Roles defined; people **UNASSIGNED** |
| Target users and top tasks | Documented |
| Public vs authenticated | Documented |
| Forbidden actions and escalation | Documented |
| Candidate public sources | Documented; **not signed by a content owner** |
| Retention policy | Documented; **not approved by privacy owner**; TTL days unresolved |
| MVP / deferred / out of scope | Documented |
| Assumptions and risks | Yes — `risk-register.md` |
| Spec conflicts recorded | Yes — not silently resolved |

**Residual risk:** Named owners and formal source/privacy sign-off are still required before production. That does not block writing foundation code later, but it **does** block claiming official production status and enabling admin ingestion.

**This phase does not include:** app scaffolding, providers, UI, or ingestion.

---

## Phase 1 — Assistant identity, conversation policy, and safety rules

**Status:** Complete as documentation (`pixel-behavior` `1.1.0`). Not loaded by running code.

**Objective:** Specify Pixel’s behavior before prompts are embedded in code.

**Delivered:**

- `docs/policies.md` — central contract (20 sections + versioning)
- `docs/safety-rules.md` — SHALL rules with eval labels
- `docs/escalation-matrix.md`
- `docs/tool-confirmation-policy.md` — conceptual; no tools implemented
- `docs/conversation-examples.md` — 102 examples
- `evals/policy/cases.jsonl` (83) and `evals/safety/cases.jsonl` (19)

**Exit:** Reviewers can predict Pixel’s response to common and hostile scenarios from these files.

**Owner approval:** Still UNASSIGNED. Policies remain draft.

**Depends on:** Phase 0.

**Do not:** start Phase 2 automatically.

---

## Phase 2 — Repository, environments, and engineering foundation

**Objective:** Reproducible monorepo with checks. Still no real AI loop required.

**Work:**

- Git, gitignore, `apps/web`, `apps/api`, `apps/worker`, `packages/*`.
- TypeScript + Python tooling: lint, format, typecheck, unit test harness.
- `.env.example` without secrets.
- Docker Compose: API + Postgres/pgvector.
- CI: lint, typecheck, unit tests, build, dependency scan.
- Health endpoints; typed settings.
- ADR template; coding standards.

**Exit:** A new engineer can clone, configure, and run empty services locally. CI blocks obvious failures.

**Does not:** implement STT/TTS/RAG beyond stubs/interfaces.

---

## Phase 3 — Conversation UX prototype

**Objective:** Visible Pixel experience with a **mock** conversation provider.

**Work:**

- Implement the state machine from `ARCHITECTURE.md`.
- Mic permission, text input, transcript, stop/mute/clear, keyboard a11y.
- Source card and action placeholders.
- Mock replies so UI is testable without backends/providers.

**Exit:** Core conversation is understandable without a manual. Every voice action has a visual/text alternative.

---

## Phase 4 — End-to-end voice loop

**Objective:** Smallest **real** path: mic → STT → short answer → TTS → barge-in.

**Work:**

- `SpeechToTextProvider` / `TextToSpeechProvider` + mock + first real adapter.
- WebSocket transport; playback queue; cancel.
- Latency metrics per stage.
- Credentials never in the browser.

**Exit:** Multiple consecutive voice turns; barge-in stops audio; text fallback still works.

**Note:** Answers may still be generic/safe, not Cyber Florida RAG.

---

## Phase 5 — AI orchestrator and conversation state

**Objective:** One controlled boundary for intent, context, retrieval flags, tools, style.

**Work:**

- Typed models; bounded history; policy version loading.
- Intent router; timeouts; retries; cancellation.
- Output validation hooks; fallbacks.
- Persist `conversations` / `messages`.

**Exit:** All AI requests go through the orchestrator. Context is testable with mocks.

---

## Phase 6 — Cyber Florida knowledge ingestion and RAG

**Objective:** Org-specific answers grounded in approved content.

**Work:**

- Source registry, extract/clean/chunk/embed, pgvector search.
- Untrusted evidence wrapping.
- Citations in UI.
- Eval set of Cyber Florida questions.
- Refresh/delete.

**Exit:** Eval hit-rate/groundedness measured. Deleted sources disappear. RAG cannot grant tools.

---

## Phase 7 — Tools, actions, and program navigation

**Objective:** Safe next steps, not only answers.

**Work:**

- Tool interface, allowlisted `navigate_to_url`, find program/resource.
- Server-side validation, confirmation, `tool_executions`.

**Exit:** No arbitrary URL execution. Unauthorized users cannot use privileged tools.

---

## Phase 8 — Security, privacy, and abuse resistance

**Objective:** Harden before broad testing.

**Work:**

- Implement `SECURITY.md` controls: rate limits, CSP, redaction, injection tests, kill switches, secret rotation docs.
- Confirm admin fail-closed.

**Exit:** Critical findings fixed. Sensitive values absent from standard logs.

---

## Phase 9 — Product quality and frontend polish

**Objective:** Cyber Florida-ready UI.

**Work:** Visual identity, responsive behavior, source cards, error/empty states, a11y review, audio polish.

**Exit:** State always understandable. No core flow is pointer-only or audio-only.

---

## Phase 10 — Observability and operations

**Objective:** Production supportability.

**Work:** Structured events, dashboards, alerts, `feedback` table + `POST /v1/feedback` (FR-20), feedback review UI/report, ingestion failure visibility, runbooks.

**Exit:** A failed turn is diagnosable without raw sensitive content.

---

## Phase 11 — Comprehensive testing and evaluation

**Objective:** Prove correctness, safety, and failure behavior.

**Work:** Unit, integration, E2E, RAG eval, red-team, load, a11y, failure injection.

**Exit:** No release-blocking defects. Quality/safety thresholds met.

---

## Phase 12 — Staging pilot

**Objective:** Limited real users on production-like config.

**Work:** Seed approved sources; collect feedback; fix high-frequency failures; extend evals.

**Exit:** Stakeholders accept known limitations.

---

## Phase 13 — Production release

**Objective:** Controlled launch with rollback.

**Work:** Separate prod secrets/data; migrations; smoke tests; canary if possible; privacy notices; version all of: app, policy, model config, index.

**Exit:** Smoke tests pass; monitoring owned; rollback verified.

---

## Phase 14 — Continuous improvement

**Objective:** Measured improvement, not prompt thrash.

**Work:** Feedback review, content refresh, regression evals, retire stale sources/tools, periodic privacy/security review.

**Exit (ongoing):** Material incidents produce a test, control, or documented decision.

---

## First vertical slice (do not invert)

Build this before a large RAG corpus or decorative UI:

1. Web page with microphone + text box  
2. User speaks or types  
3. Transcript appears  
4. Backend returns one short answer  
5. Answer is spoken  
6. User interrupts → audio stops → new turn starts  

Then replace the generic answer with Cyber Florida RAG (Phase 6).

---

## Phase gate (every phase)

Before calling a phase complete:

1. Inspect repo and prior docs.  
2. Reuse existing modules; no duplicate systems.  
3. No hardcoded secrets.  
4. Tests for important new behavior.  
5. Run relevant tests, lint, typecheck, production build.  
6. Fix issues introduced by the phase.  
7. Update documentation.  
8. Report the standard **PHASE COMPLETE** block.  
9. **Do not automatically start the next phase.**

---

## Ready for Phase 2?

**YES** to begin engineering foundation when you explicitly say **Proceed to Phase 2.**

**NO** for treating Pixel as implemented, enabling admin ingestion, or production.

**NO** for loading these policies into a live model until Phase 5+ with mocks labeled as mocks.

Owner sign-off of `pixel-behavior` `1.1.0` remains UNASSIGNED.
