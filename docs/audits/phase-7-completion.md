# PIXEL PHASE 7 COMPLETION REPORT

PHASE:
Phase 7 — Tools, Actions and Program Navigation

STATUS:
PASS

DATE:
2026-08-17

OBJECTIVE:
Build Pixel’s controlled action layer so the assistant can discover approved Cyber Florida programs/resources and offer approved navigation, without giving the model unrestricted authority.

PREVIOUS PHASES REVIEWED:
YES (Phases 0–6 product, policy, orchestrator, RAG, and voice docs)

PHASES 4–6 AUDIT REVIEWED:
YES (`docs/audits/phases-4-6-engineering-audit.md`)

AUDIT BLOCKERS RESOLVED:
YES (prior HIGH: untrusted RAG evidence wrapping in the OpenAI adapter). No remaining CRITICAL/HIGH from that audit in the Phase 7 path.


FILES CREATED:

- `packages/pixel/pixel/tools/types.py`
- `packages/pixel/pixel/tools/registry.py`
- `packages/pixel/pixel/tools/validate.py`
- `packages/pixel/pixel/tools/policy.py`
- `packages/pixel/pixel/tools/urls.py`
- `packages/pixel/pixel/tools/catalog.py`
- `packages/pixel/pixel/tools/handlers.py`
- `packages/pixel/pixel/tools/runner.py`
- `packages/pixel/pixel/tools/select.py`
- `docs/tools.md`
- `docs/decisions/0012-tools.md`
- `packages/pixel/tests/test_tools_registry.py`
- `packages/pixel/tests/test_tools_urls.py`
- `packages/pixel/tests/test_tools_find.py`
- `packages/pixel/tests/test_tools_navigate.py`
- `packages/pixel/tests/test_tools_orchestrator.py`
- `packages/pixel/tests/test_tools_cancel.py`
- `docs/audits/phase-7-completion.md`

FILES MODIFIED:

- `packages/pixel/pixel/tools/__init__.py`
- `packages/pixel/pixel/orchestrator/process.py`
- `packages/pixel/pixel/orchestrator/session.py`
- `packages/pixel/pixel/orchestrator/intents.py`
- `packages/pixel/pixel/orchestrator/fallbacks.py`
- `packages/pixel/pixel/orchestrator/policy.py`
- `packages/pixel/pixel/domain.py`
- `apps/api/pixel_api/settings.py`
- `apps/api/pixel_api/voice.py`
- `apps/api/tests/test_voice.py`
- `apps/web/src/components/RecommendedAction.tsx`
- `apps/web/e2e/conversation.spec.ts`
- `packages/pixel/tests/test_intents.py`
- `packages/pixel/tests/test_session.py`
- `.env.example`, `.env.development.example`, `.env.staging.example`, `.env.production.example`
- `README.md`, `docs/ARCHITECTURE.md`, `docs/DATA_FLOW.md`, `docs/ROADMAP.md`, `docs/orchestrator.md`, `docs/policies.md`, `docs/tool-confirmation-policy.md`, `docs/README.md`, `docs/decisions/README.md`

Also present in the working tree from the Phases 4–6 audit (not Phase 7 scope): `packages/pixel/pixel/providers/openai.py`, related tests, `docs/knowledge.md`, `docs/voice.md`, and `docs/audits/phases-4-6-engineering-audit.md`.


TOOL ARCHITECTURE:
Orchestrator selects tools deterministically (`select_tool_calls`). The model does not execute tools and does not receive a tool-calling API. Execution is `production_registry()` → permission → confirmation → schema validation → handler → `NormalizedToolResult`. Retrieved documents are data only.

TOOL REGISTRY:
PASS

TOOL INTERFACE:
PASS (name, description, version, input fields, permission, confirmation, timeout, allowlist, audit, side-effect level)

TOOL INPUT VALIDATION:
PASS (required fields, types, enums, length, extra fields rejected)

TOOL OUTPUT VALIDATION:
PASS (`NormalizedToolResult` / `ToolResult`; handlers do not return raw provider objects)

UNKNOWN TOOL REJECTION:
PASS (`run_shell_command` → `unknown_tool`; no dynamic import)


TOOLS IMPLEMENTED:

navigate_to_url:
PASS

find_program:
PASS

find_resource:
PASS

search_approved_content:
PASS (wraps Phase 6 `Retriever` / `fixture_retriever()`)

OTHER APPROVED TOOLS:
- None in production. Explicit-confirmation engine is unit-tested with a non-production `side_effect_demo` definition.


NAVIGATION SECURITY:

DOMAIN ALLOWLIST:
PASS (`cyberflorida.org`, `www.cyberflorida.org` via parsed hostname)

URL PARSING:
PASS (`urllib.parse`; no substring host checks)

UNSAFE SCHEMES BLOCKED:
PASS (`javascript:`, `data:`, `file:`, `http:`)

ARBITRARY URL TEST:
PASS (`https://attacker.example` denied; no action href)

SSRF REVIEW:
PASS (tools do not fetch URLs; localhost / private / metadata hosts denied; unregistered paths on the approved host denied)


AUTHORIZATION:

SERVER-SIDE PERMISSION CHECK:
PASS (`AuthContext` from the API; public only in this phase)

MODEL CAN GRANT PERMISSION:
NO

RETRIEVED CONTENT CAN GRANT PERMISSION:
NO


CONFIRMATION:

CONFIRMATION POLICY:
PASS (lookups `none`; navigation `ui_click` via labeled Open link; no auto-redirect)

CONFIRMATION TESTS:
PASS (explicit policy unit-tested; confirmation is not reusable across tools)


TOOL ORCHESTRATOR INTEGRATION:
PASS

TOOL LOOP LIMIT:
PASS (`MAX_TOOL_CALLS_PER_TURN`, default 2)

TOOL TIMEOUT:
PASS (`TOOL_TIMEOUT_SECONDS`, default 5; executor does not block the turn on timeout)

TOOL CANCELLATION:
PASS

STALE TOOL RESULT PROTECTION:
PASS (cancelled flag raises `CancelledError`; generation/commit ignores stale turns)


TOOL AUDIT EVENTS:
PASS (`tool_audit` logs name, status, authorized, confirmed, duration, session, turn, correlation; arguments are not logged)

ACTION UI INTEGRATION:
PASS (Open chips use canonical approved hrefs; aria-label includes hostname)


PROGRAM DISCOVERY:
PASS (students → CyberWorks + SECCDC)

RESOURCE DISCOVERY:
PASS

SOURCE / ACTION CONSISTENCY:
PASS (follow-up open uses `last_offers` from the same approved sources)


PROMPT-INJECTION TOOL TESTS:
PASS

UNKNOWN TOOL ATTACK:
PASS

UNAPPROVED URL ATTACK:
PASS

FAKE CONFIRMATION ATTACK:
PASS


RAG REGRESSION:
PASS (knowledge eval 122 cases; groundedness 1.0; hit@3 0.945)

CITATION REGRESSION:
PASS (citation_correctness 0.908)

TEXT REGRESSION:
PASS (pytest + API TestClient)

VOICE REGRESSION:
PASS at API/orchestrator layer (`test_websocket_voice_turn`). Playwright UI not re-run in this environment (Chromium missing).

BARGE-IN REGRESSION:
PASS at cancellation/unit layer. Playwright barge-in UI not re-run in this environment.


SECURITY CHECK:
No arbitrary HTTP/shell/SQL tools. Navigation is registered canonical HTTPS URLs only. Authorization is server-side. Retrieved text cannot invoke tools.

PRIVACY CHECK:
Tool audit logs do not include arguments, transcripts, or secrets. Tools receive only validated fields plus session/turn/correlation ids.

ACCESSIBILITY CHECK:
Open links have accessible names including destination hostname; keyboard-focusable anchors; no voice-only navigation.

SECRET SCAN:
PASS


TESTS RUN:

```
python -m ruff format packages/pixel apps/api apps/worker
python -m ruff check packages/pixel apps/api apps/worker
python -m pyright
python -m pytest
python -c "from pixel.knowledge.evaluate import default_cases_path, evaluate, load_cases; print(evaluate(load_cases(default_cases_path())))"
npm run web:format:check
npm run web:lint
npm run web:typecheck
npm run web:test
npm run web:build
python -m pip_audit
npm audit --audit-level=high
npm run web:e2e   # failed: Playwright Chromium not installed in this agent environment
FastAPI TestClient flow for students → first program → open → attacker deny
```

TEST RESULTS:

- ruff format/check: PASS
- pyright: 0 errors
- pytest: **127 passed, 1 skipped** (postgres; `PIXEL_TEST_DATABASE_URL` unset)
- knowledge eval: 122 cases, groundedness 1.0, hit@3 0.945, abstention 0.923
- prettier/eslint/tsc: PASS
- vitest: 37 passed
- next build: PASS
- pip-audit: no known vulnerabilities
- npm audit --audit-level=high: 0 vulnerabilities
- Playwright: NOT VERIFIED (browser binary missing; install blocked in this environment)
- In-process E2E: students → CyberWorks/SECCDC → Open CyberWorks; attacker.example denied

BUILD RESULT:
PASS (`next build`)

LINT RESULT:
PASS (ruff + eslint)

TYPE CHECK RESULT:
PASS (pyright + tsc)


ISSUES FOUND:

- Follow-up “Tell me more about the first one.” was not classified as a follow-up, so later “Open that program.” lost context.
- Empty later turns overwrote `session.last_offers`.
- Student audience filter treated every source as matching because “students” was added to the allowed set unconditionally.
- Tool timeout used `ThreadPoolExecutor` as a context manager, which waited for the slow worker after timeout.

ISSUES FIXED:

- Follow-up regex covers “tell me more about the first/second/third one”.
- `commit_turn` preserves prior offers when the new turn has none.
- Student audience matches only `students` and `career-seekers`.
- Timeout returns immediately (`shutdown(wait=False)`).
- Lookup tool actions are not merged with unrelated RAG Open chips.

KNOWN ISSUES:

- Live OpenAI STT/TTS/LLM still unverified without `OPENAI_API_KEY`.
- Postgres/pgvector still unverified without `PIXEL_TEST_DATABASE_URL`.
- Playwright Chromium was not available in this agent environment, so browser E2E/voice/barge-in UI was not re-run here. Equivalent API and unit coverage passed.

NOT VERIFIED:

- Playwright Chromium UI (text, voice PTT, barge-in) in this session
- Live vendor providers
- Docker/postgres integration

TECHNICAL DEBT:

- Stronger idempotency for write tools is deferred until side-effecting tools exist.
- Timed-out worker threads are abandoned (`wait=False`) rather than hard-killed.
- Sessions remain in-memory (ADR-0005 deferred).
- No dedicated axe-core suite (same as prior phases).


PHASE 7 EXIT CRITERIA:
PASS

READY FOR PHASE 8:
YES

REASON:
Approved low-risk tools are registered, schema-validated, permission-checked, allowlisted, audited, and wired through the orchestrator. Arbitrary URLs, unknown tools, prompt-injection navigation, and model/retrieved permission grants are denied. RAG/citation metrics are unchanged. Browser Playwright was not re-run here due to a missing Chromium binary; API-level E2E covers the required program-navigation flow.


NEXT RECOMMENDED ACTION:

Wait for explicit instruction: `Proceed to Phase 8.`

Proceed to Phase 8 — Security, Privacy and Abuse Resistance.
