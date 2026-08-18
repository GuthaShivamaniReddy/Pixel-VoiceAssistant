# Pixel — Orchestrator (Phase 5–6)

**Status:** Implemented. This describes the running path, not a future design.

## Boundary

All assistant intelligence goes through `pixel.orchestrator.process.process_turn`.

```
Voice PCM → STT → transcript ─┐
                              ├→ process_turn → retrieval (if required) → AssistantResponse → optional TTS
Text ─────────────────────────┘
```

API routes (`POST /v1/turns`, `WS /v1/realtime`) do not call the LLM themselves. Frontend components never call a provider SDK.

## Request flow

1. Validate and bound the user text.
2. Load session context (last 8 messages, last intent).
3. Classify intent (deterministic rules).
4. If `cyberflorida_knowledge`, retrieve from the approved index. Missing evidence abstains; the model is not asked to guess.
5. Load server-side policy `pixel-behavior` `1.5.0`.
6. Call `LLMProvider` with a normalized `LlmRequest` (evidence is untrusted data), or use a canned refusal/abstention when `skip_model` is set.
7. Validate output (empty, length, secret/policy leak).
8. Attach allowlisted sources/actions from retrieval or tools. Model output cannot grant tools or extra URLs.
9. Optional TTS.

Tool details: `docs/tools.md`.

## Session state

In-memory `SessionStore` (ADR-0009). Server-generated ids. Sliding TTL default 1800 seconds. Max 8 messages (4 turns). Clear Conversation calls `POST /v1/sessions/{id}/clear`.

Postgres remains the intended system of record (ADR-0005). Knowledge tables exist (Phase 6); conversation tables are not created yet.

## Intent taxonomy

`cyberflorida_knowledge` · `cybersecurity_help` · `scam_help` · `navigation` · `clarification` · `unsupported`

Routing is deterministic (ADR-0010). Org questions set `requires_retrieval=True` and must retrieve. Navigation sets `requires_tool=True` and runs `navigate_to_url` through the registry (ADR-0012).

## Timeouts and retries

Provider HTTP timeouts come from settings (`LLM_TIMEOUT_SECONDS`, etc.). LLM calls retry at most once for timeout, rate-limit, or connection errors. Auth failures, invalid requests, cancellation, and policy refusals are not retried. Backoff is 0.2s then 0.4s.

## Cancellation

Turn ids plus `CancellationFlag`. A newer `begin_turn` cancels the previous flag and increments `generation`. Late results cannot commit if `generation` no longer matches. Retrieval does not bypass barge-in.

## Fallbacks

Empty or invalid model text becomes a short retry message. Provider errors are mapped to `timeout`, `network`, `response_failure`, or `cancelled`. Users never see stack traces or API keys. Missing org evidence uses the abstention copy.

## Policy

Authoritative prompt: `packages/pixel/pixel/orchestrator/policy.py`. Users cannot override it. Retrieved documents cannot override it. Frontend does not contain the system policy.

Knowledge details: `docs/knowledge.md`.
