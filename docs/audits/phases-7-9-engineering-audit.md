# PIXEL ENGINEERING AUDIT

AUDIT RANGE:
Phases 7–9

DATE:
2026-08-17

BRANCH:
main

COMMIT:
`78c94f40c8d78a76cff76c586e6bf31a9209e03b` (`fix: pin jsdom 26 so Vitest can run on Node 20 CI`)

WORKING TREE:
Dirty. Phases 7–9 implementation and this audit’s fixes are uncommitted. Valid existing work was preserved.

AUTHORITATIVE SPEC:
`Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` was **not present in the workspace**. Audit used `docs/product.md`, `docs/ARCHITECTURE.md`, `docs/policies.md`, `docs/tools.md`, `docs/security/`, `docs/runbooks/`, prior audits, and the running code.

PREVIOUS COMPLETION REPORTS:
Reviewed and **not trusted as evidence**. Claims were re-checked against implementation, tests, and runtime.

---

## PIXEL PHASES 7–9 AUDIT PLAN (executed)

AUDIT RANGE: Phases 7–9

CURRENT BRANCH: main

CURRENT COMMIT: `78c94f40c8d78a76cff76c586e6bf31a9209e03b`

WORKING TREE: Uncommitted Phase 7–9 work plus this audit’s fixes

PHASE 7 AREAS TO VERIFY:
Registry, schemas, server validation/authz/confirmation, allowlist/SSRF, unknown tools, loop limit, cancel/stale, program discovery, RAG/tool consistency, injection.

PHASE 8 AREAS TO VERIFY:
Threat model vs code, secrets, admin, IDOR, injection, rate/size/CORS/headers, XSS, SQL, redaction, retention, kill switches, runbooks, dependency scans.

PHASE 9 AREAS TO VERIFY:
Mascot identity, truthful states, voice/TTS/barge-in, sources/actions, warning/uncertainty/errors, responsive, a11y, performance, regressions.

KNOWN RISKS:
In-process rate limits; HTTP turns do not stream retrieval; local STT/TTS may be mock; PDF missing from repo.

---

========================================
EXECUTIVE SUMMARY

OVERALL RESULT:
PASS

OVERALL SCORE:
91/100

READY FOR PHASE 10:
YES

This audit verified a server-side tool registry, strict navigation allowlist, fail-closed admin, prompt-injection and indirect-injection resistance, no provider secrets in the browser bundle, and a custom Pixel mascot whose listening/speaking poses follow real assistant state. Playwright confirmed text, RAG citations, tools, barge-in, keyboard, and mobile.

No CRITICAL or HIGH findings remain after audit fixes.

========================================
PHASE 7 — TOOLS

STATUS:
PASS

SCORE:
93/100

TOOL REGISTRY:
PASS — `production_registry()` is the only production set: `find_program`, `find_resource`, `search_approved_content`, `navigate_to_url`. Duplicate names rejected.

INPUT VALIDATION:
PASS — server-side `validate_arguments` (types, enums, extra fields, length, required, null).

OUTPUT VALIDATION:
PASS — handlers return `NormalizedToolResult`; non-instances become `internal_error`.

AUTHORIZATION:
PASS — `AuthContext` is constructed in the API as `permission="public"`. Client JSON cannot raise it. Privileged test tools are denied for public auth even with fake confirmation.

CONFIRMATION:
PASS — `explicit` requires matching `confirmed_tool`. Production `navigate_to_url` uses `ui_click` (labeled link is the confirmation; Pixel does not auto-redirect). No write tools exist in production.

NAVIGATION ALLOWLIST:
PASS — `urlparse` + host allowlist + registered canonical URL. Tested: approved FirstLine; `attacker.example`; `javascript:`; `data:`; `https://cyberflorida.org.attacker.example`; localhost; metadata IP; unregistered path on cyberflorida.org.

SSRF:
PASS — ingest fetch requires approved HTTPS canonical URL, no redirects, private-host check. Tools do not fetch URLs.

UNKNOWN TOOL REJECTION:
PASS — `run_shell_command`, `delete_database`, `http_request`, `admin_override` → `unknown_tool`.

TOOL LOOP LIMIT:
PASS — `MAX_TOOL_CALLS_PER_TURN` default 2; selection slices to `max_calls`. Deterministic `select_tool_calls`; the model has no tool-calling API.

CANCELLATION:
PASS — `CancellationFlag` abort; stale `commit_turn` generation check. Audit fix: HTTP/WS now return cancelled (409 / `cancelled`) if commit is rejected, so a late tool result cannot update session or be delivered as a successful turn.

AUDIT EVENTS:
PASS — `tool_audit` logs name/status/authorized/confirmed/duration/session/turn/correlation. Arguments are not logged.

PROGRAM DISCOVERY:
PASS — audience mapping (student/educator/business/public sector/beginner) against approved registry; inactive sources excluded; no invented programs (`not_found`).

RESOURCE DISCOVERY:
PASS — `find_resource` / `search_approved_content` over public approved sources only.

RAG / TOOL CONSISTENCY:
PASS with residual — follow-up “open that program” stays on the offered URL (`test_students_then_open_first_program`, Playwright). When RAG and `find_program` both run, actions prefer tool results and sources are merged by URL, so an extra RAG card can appear beside program actions.

PROMPT-INJECTION TOOL TESTS:
PASS — attacker URLs denied; “I already confirmed”; retrieved poison; multi-turn social engineering; client `isAdmin` headers.

EXIT CRITERIA:
PASS

ISSUES:
- MEDIUM: RAG+tool merge can list an extra RAG source beside tool actions.
- LOW: `ui_click` auto-satisfies runner confirmation (documented; browser click is the real confirmation).

FIXES:
- HTTP/WS stale commit no longer returns a successful body.
- Added deny tests for `data:`, lookalike host, additional unknown tools, null arguments.

========================================
PHASE 8 — SECURITY / PRIVACY

STATUS:
PASS

SCORE:
91/100

THREAT MODEL:
PASS — `docs/security/threat-model.md` matches this repo (browser, mic, WS, API, sessions, orchestrator, providers, RAG, tools, admin, DB, logs, CI, secrets).

SECRET MANAGEMENT:
PASS — `.env` gitignored; examples empty; `NEXT_PUBLIC_*` secret-shaped names throw; production build has no `OPENAI_API_KEY` / live OpenAI key material / `ADMIN_TOKEN`; repo secret scan and git history scan pass.

REALTIME TOKEN SECURITY:
PASS / N/A — browser talks to Pixel `WS /v1/realtime`, not a vendor realtime API. Long-lived provider keys stay on the server.

SERVER AUTHORIZATION:
PASS — sessions are UUID capability tokens; unknown session 404; expired 410; AuthContext not client-supplied.

ADMIN SECURITY:
PASS — empty token → 403 `admin_disabled` even if `ADMIN_ENABLED`; missing/wrong bearer → 401; valid token on unknown path → 404 (no admin implementation yet). Client `isAdmin` / `X-Admin` ignored.

PROMPT INJECTION:
PASS — evals + API + Playwright.

INDIRECT PROMPT INJECTION:
PASS — poison fixture ingest; retrieved content cannot authorize tools or attacker URLs.

RAG ACCESS CONTROL:
PASS — retriever ignores caller `access_class`; public search cannot retrieve `internal` chunks; deactivate_source removes from retrieval.

RATE LIMITS:
PASS (in-process) — sessions 429 below/above limit tested. Not distributed. Docs state this.

REQUEST LIMITS:
PASS for `Content-Length` 413. Residual: body size is not re-measured if `Content-Length` is omitted/lied about.

INPUT VALIDATION:
PASS — Pydantic field lengths, session id length, WS control byte cap, correlation-id UUID replacement.

CORS:
PASS — explicit origins; `*` rejected at settings; credentials false; unknown origin has no ACAO; WS origin checked (required in production).

SECURITY HEADERS:
PASS — inspected on TestClient `/health`: CSP `frame-ancestors 'none'`, nosniff, DENY, no-referrer, Permissions-Policy. HSTS in production settings. Next.js sets matching browser headers.

XSS:
PASS — React text nodes; no `dangerouslySetInnerHTML` / `innerHTML` in app code; unit test encodes `<script>`.

SSRF:
PASS — see Phase 7.

SQL INJECTION REVIEW:
PASS — pgvector access uses parameterized `psycopg` queries; user text is a bound embedding literal, not concatenated SQL.

LOG REDACTION:
PASS — unit tests for keys/tokens/OTP/DB URLs; turn logs use ids/intent/status, not transcripts or audio.

DATA RETENTION:
PASS vs current docs — in-memory sessions, TTL 1800s, no feedback store, no audio DB. Institutional retention days remain UNASSIGNED (documented).

RAW AUDIO PRIVACY:
PASS — bounded PCM on active turn; discarded on take/cancel; OpenAI STT (if configured) is vendor processing, documented separately.

DEPENDENCY SCANNING:
PASS — `npm audit` 0 vulnerabilities; `pip-audit` no known issues (local `pixel` package skipped as not on PyPI).

KILL SWITCHES:
PASS — `KillSwitch` blocks tools/providers/knowledge in orchestrator tests. Changes require process restart (documented).

INCIDENT RUNBOOKS:
PASS as usable engineering procedures with UNASSIGNED owners. Cover detection, triage, containment, provider/tool/source disablement, rotation, recovery.

EXIT CRITERIA:
PASS

ISSUES:
- MEDIUM: in-process rate limiter (honest in code/docs).
- MEDIUM: size limit trusts `Content-Length`.
- MEDIUM: kill switches are env/restart, not a live admin UI.
- LOW: log/audit retention days UNASSIGNED.

FIXES:
- Removed unreachable duplicate HTTP GET in `pixel.knowledge.fetch`.

========================================
PHASE 9 — PRODUCT QUALITY

STATUS:
PASS

SCORE:
88/100

PIXEL MASCOT QUALITY:
PASS — original SVG (`PixelCharacter.tsx`): monitor head, digital face, antennas, white/green armor, articulated body, pixel-art. Reference PNG is not loaded.

REALISTIC VA BEHAVIOR:
PASS with caveat — idle/listen/think/speak/read/tool-present/success/warning/uncertain/error/offline/muted/recover map from real assistant signals. Searching and in-flight tool poses are implemented in the mapper but hardcoded `false` in `useMascotCues` because HTTP `/v1/turns` does not stream retrieval/tool start. That is truthful (not fake search). Users therefore cannot visually distinguish thinking vs searching on the live HTTP path.

PIXEL SPEAKS BACK:
PASS (path) — mock/local TTS returns WAV; Playwright PTT reaches speaking; `audio_wav_base64` present on `/v1/turns` with `speak: true`.

TTS / ANIMATION SYNC:
PASS — speaking animation starts on playback `onStart`; mouth/level from analyser; stop/barge-in increment playback generation.

LISTENING UX:
PASS — “Listening…” text, mic `data-mic`, posture, waveform CSS var (not per-frame React state).

THINKING UX:
PASS — processing → thinking.

SEARCHING UX:
PARTIAL — mapper exists; live HTTP never sets `retrievalActive`.

SOURCE READING:
PASS — speaking + sources → reading; cards labeled Approved / Mock / Official, never invented “VERIFIED”.

BARGE-IN UX:
PASS — Playwright: speaking/processing → interrupt → listening; playback stop.

SOURCE CARDS:
PASS — title, kicker, official link, overflow wrap, keyboard link name, long-description expand.

TOOL ACTION UI:
PASS — allowlisted chips; Playwright open-program; attacker URL has no href.

SECURITY WARNING UX:
PASS — “I clicked a suspicious link” uses warning kicker, not error; no delay-for-animation.

SCAM UX:
PASS — calibrated “warning signs, not a verdict” when scam/containment language is present.

UNCERTAINTY UX:
PASS — distinct from error (`cannot verify`).

ERROR UX:
PASS — What happened / What you can do; Try again / Use text / Return to ready.

DESKTOP / TABLET / MOBILE / SMALL MOBILE:
PASS — 900px stack, 640px compact Pixel (8rem), 380px full-width controls; Playwright 390×844 no overflow.

ACCESSIBILITY:
PASS for implemented checks — labels, skip link, keyboard send, focus after send/clear not on first idle, 3px focus, contrast (secondary 6.99:1, primary 15.4:1, buttons 9.57:1). Automated axe not in repo.

REDUCED MOTION:
PASS — `data-reduced`, static poses, UI transitions disabled.

PERFORMANCE:
PASS for Phase 9 — mic/speech levels write CSS variables; playback generation guard.

EXIT CRITERIA:
PASS with documented searching limitation.

ISSUES:
- MEDIUM: searching/tool-running poses unused on HTTP turns.
- MEDIUM: audible live-vendor TTS not heard in this audit environment.
- LOW: no axe-core / Firefox / Safari automation.

FIXES:
None required as HIGH. No fake-state animations added.

========================================
ISSUES FOUND

CRITICAL:
- none

HIGH:
- none remaining

MEDIUM:
- In-process (not distributed) rate limiting
- Request size limit uses Content-Length only
- Live HTTP UI cannot show Searching vs Thinking (no retrieval-started signal)
- RAG+tool merge may attach an extra RAG source beside program actions
- Kill switches require API restart
- Live vendor TTS not audibly verified here

LOW:
- Institutional retention days UNASSIGNED
- No axe-core suite
- Chromium-only e2e
- `ui_click` confirmation is runner-auto (browser click is the control)
- Some product docs still describe earlier phase mock status in historical sections

========================================
ISSUES FIXED:
- Unreachable duplicate fetch after `return` in `pixel.knowledge.fetch`
- Successful HTTP/WS bodies no longer returned when `commit_turn` rejects a stale generation
- Added navigation denies: `data:` and `cyberflorida.org.attacker.example`
- Unknown-tool coverage expanded (`delete_database`, `http_request`, `admin_override`)
- Null tool argument rejected in tests

========================================
FILES MODIFIED:
- `packages/pixel/pixel/knowledge/fetch.py`
- `apps/api/pixel_api/voice.py`
- `packages/pixel/tests/test_tools_urls.py`
- `packages/pixel/tests/test_tools_navigate.py`
- `packages/pixel/tests/test_tools_find.py`
- `docs/audits/phases-7-9-engineering-audit.md` (this file)

========================================
TESTS RUN

COMMAND: `python -m ruff format --check apps/api apps/worker packages/pixel`
RESULT: PASS (98 files)

COMMAND: `python -m ruff check apps/api apps/worker packages/pixel`
RESULT: PASS

COMMAND: `python -m pyright`
RESULT: PASS (0 errors)

COMMAND: `python -m pytest`
RESULT: 166 passed, 1 skipped (Postgres unless `PIXEL_TEST_DATABASE_URL`)

COMMAND: `npm run web:format:check`
RESULT: PASS

COMMAND: `npm run web:lint`
RESULT: PASS

COMMAND: `npm run web:typecheck`
RESULT: PASS

COMMAND: `npm run web:test`
RESULT: 67 passed

COMMAND: `npm run web:e2e`
RESULT: 13 passed (Chromium: text, voice PTT, barge-in, RAG, tools, injection, keyboard, mobile, warning UX)

COMMAND: `npm run web:build`
RESULT: PASS

COMMAND: secret scan (included in pytest `test_secret_scan.py`)
RESULT: PASS (no live secret markers; git history clean for private-key / sk-live / sk-proj)

COMMAND: `npm audit`
RESULT: 0 vulnerabilities

COMMAND: `python -m pip_audit`
RESULT: No known vulnerabilities (local package `pixel` skipped as not on PyPI)

COMMAND: axe-core
RESULT: NOT VERIFIED — not a project dependency

COMMAND: Live microphone + speaker TTS with OpenAI keys
RESULT: NOT VERIFIED — workspace providers default mock; no live key used in this audit

COMMAND: Firefox / Safari e2e
RESULT: NOT VERIFIED — Playwright project is Chromium only

========================================
TEST RESULTS

PASSED:
166 pytest, 67 Vitest, 13 Playwright, format/lint/types, next build, secret scan, npm audit, pip-audit

FAILED:
0

SKIPPED:
1 pytest (Postgres knowledge store)

NOT VERIFIED:
axe-core; live vendor audible TTS; Firefox/Safari; distributed rate-limit behavior; PDF spec file (missing from workspace)

========================================
VOICE

PIXEL HEARS USER:
PASS (PTT PCM → WS STT; Playwright fake microphone)

PIXEL SPEAKS BACK:
PASS (WAV on speak=true; playback engine; speaking state)

AUDIBLE TTS MANUALLY VERIFIED:
NO

BARGE-IN:
PASS

OLD AUDIO RESUMES:
NO (queue stop + generation token)

DUPLICATE AUDIO:
NO (queue replaces active turn)

========================================
SECURITY

SECRET SCAN:
PASS

AUTHORIZATION:
PASS

PROMPT INJECTION:
PASS

INDIRECT INJECTION:
PASS

TOOL SECURITY:
PASS

ADMIN SECURITY:
PASS

========================================
PRIVACY

RAW AUDIO:
Transient in-memory PCM; not stored in DB/disk by Pixel

TRANSCRIPTS:
In-memory session, max 8 messages, TTL/clear/restart

LOG REDACTION:
Implemented and unit-tested

RETENTION:
Matches `docs/security/data-retention.md`; institutional day counts UNASSIGNED

========================================
ACCESSIBILITY

KEYBOARD:
PASS

FOCUS:
PASS

CONTRAST:
PASS (measured token pairs all ≥ 5.5:1)

SCREEN READER:
PASS for labels/status (one polite live region); full AT pass NOT VERIFIED with NVDA/VoiceOver

REDUCED MOTION:
PASS (code + unit)

========================================
RESPONSIVE

DESKTOP:
PASS

TABLET:
PASS

MOBILE:
PASS

SMALL MOBILE:
PASS (CSS ≤380px; e2e 390×844)

========================================
FALSE COMPLETION FINDINGS:
- Phase 9 completion listed SEARCHING as PASS. The mapper is real, but the running HTTP UI never enters searching (`retrievalActive: false`). This audit scores Searching UX as PARTIAL, not a fake-animation failure.
- Rate limiting works but is process-local. Docs are honest; do not describe it as distributed.

========================================
PLACEHOLDER / MOCK FINDINGS:
- Local `LLM/STT/TTS_PROVIDER=mock` is intentional without keys. Not a hidden production mock in the tool/security path.
- Frontend `mock-provider.ts` is for unit tests; live UI uses `/v1/turns`.
- Source cards labeled “Mock source — not live RAG” only when provenance is mock.
- No TODO/FIXME/LOREM in `apps/` application TS/Python for Phase 7–9 paths.

========================================
REMAINING TECHNICAL DEBT:
- Stream retrieval/tool-start to the client if Searching/Tool-running poses should appear during HTTP turns
- Distributed rate limiting (ops)
- Body-length verification beyond Content-Length
- axe-core + multi-browser e2e
- Named privacy/security owners and retention days

========================================
DEFERRED ISSUES:
- Phase 10 observability / feedback endpoint
- Hot admin UI for kill switches
- SSO / authenticated permission rank (all public Q&A is `public`)
- Write tools with explicit confirmation (engine exists; no production write tool)

========================================
REGRESSION RISKS:
- Streaming retrieval later must not fake searching
- Do not add model-controlled tool execution
- Do not put vendor keys in `NEXT_PUBLIC_*`
- Keep barge-in playback generation when changing the mascot

========================================
FINAL VERDICT

PHASE 7:
PASS

PHASE 8:
PASS

PHASE 9:
PASS

OVERALL:
PASS

READY FOR PHASE 10:
YES

REASON:
Controlled tools, server authorization, injection resistance, secrets, and core UX/voice/RAG/tool regressions are verified. Remaining items are operational (observability, distributed limits, live-vendor audio hearing) and named-owner gaps — appropriate for Phase 10+, not blockers.

NEXT RECOMMENDED ACTION:
Wait for explicit instruction: Proceed to Phase 10.
