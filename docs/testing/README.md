# Testing strategy

**Current test status (Phases 2–9):** Python pytest (API/orchestrator/knowledge/providers/security), Vitest (web), Playwright Chromium E2E for text, starters, keyboard send, mobile layout, voice PTT, barge-in, follow-ups, clear, injection, tool navigation, and warning UX. CI runs format, lint, typecheck, tests, build, Playwright, pip-audit, npm audit, and the in-repo secret-marker scan.

## Layers (required before production)

| Layer | What to verify | Exists now |
|---|---|---|
| Unit | State transitions, mock provider, env guards, API health/CORS/admin | Yes |
| Contract | Provider adapters, API models, migrations | Partial (Postgres knowledge tests skip without `PIXEL_TEST_DATABASE_URL`) |
| Integration | message → orchestrator → retrieval → model (mocks); ingest → search | Yes (Phase 6) |
| End-to-end | Browser text + mocked listen/stop, error recovery, source cards | Yes |
| Voice quality | Domain terms, silence, interrupt | Partial (Playwright PTT + barge-in; live vendor STT not verified) |
| RAG eval | Hit rate, groundedness, abstention, freshness | Yes (fixture corpus) |
| Safety / red-team | Injection, prompt leak, tool abuse, harmful cyber, rate limits, redaction, admin authz | Yes (unit/API; live vendor model not scored) |
| Performance | Concurrent sessions, stage latency | Partial (per-turn timings including retrieval) |
| Accessibility | Keyboard, labels, transcript, contrast | Partial (unit + labels; no axe suite) |
| UAT | Real user tasks | No |

## Failure tests (mandatory later)

Microphone denied; no mic; silence; network drop; STT error; LLM timeout; empty retrieval; inactive source; TTS fail after text; tool denied; repeated barge-in; injected instructions in retrieved content; requests for prompts/credentials.

Phase 3 covers mocked network/response/timeout/empty failures plus permission-denied copy.

## CI expectation (Phase 2+)

Lint, typecheck, unit tests, build, dependency scan, Playwright Chromium E2E. RAG/safety evals on AI-changing PRs once datasets exist.

Do not add tests that require live paid APIs or a physical microphone in CI.
