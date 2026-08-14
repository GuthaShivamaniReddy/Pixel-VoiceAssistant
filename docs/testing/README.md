# Testing strategy

**Current test status:** No test runner, no tests, no coverage. `docs/GAP_ANALYSIS.md` records every runtime requirement as MISSING.

Pixel needs deterministic software tests **and** evaluation datasets (see `docs/evaluations/`).

## Layers (required before production)

| Layer | What to verify | Exists now |
|---|---|---|
| Unit | State transitions, routing, chunking, tool schemas, authz, redaction, fallbacks | No |
| Contract | Provider adapters, API models, migrations | No |
| Integration | message → orchestrator → retrieval → model (mocks); ingest → search | No |
| End-to-end | Browser text + voice states, barge-in, sources, clear session | No |
| Voice quality | Domain terms, silence, interrupt | No |
| RAG eval | Hit rate, groundedness, abstention, freshness | No |
| Safety / red-team | Injection, prompt leak, tool abuse, harmful cyber | No |
| Performance | Concurrent sessions, stage latency | No |
| Accessibility | Keyboard, labels, transcript, contrast | No |
| UAT | Real user tasks | No |

## Failure tests (mandatory later)

Microphone denied; no mic; silence; network drop; STT error; LLM timeout; empty retrieval; inactive source; TTS fail after text; tool denied; repeated barge-in; injected instructions in retrieved content; requests for prompts/credentials.

## CI expectation (Phase 2+)

Lint, typecheck, unit tests, build, dependency scan. RAG/safety evals on AI-changing PRs once datasets exist.

Do not add tests that require live paid APIs or a physical microphone in CI.
