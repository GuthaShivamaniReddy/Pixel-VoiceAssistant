# PIXEL ENGINEERING AUDIT

AUDIT RANGE:  
Phases 0–3

DATE:  
2026-08-14

BRANCH:  
`main`

COMMIT:  
`7178fc17003c2410b1eb468e0ece491739924157`  
(`docs: add Pixel Phase 0-1 product, policy, and architecture blueprint`)

WORKING TREE:  
Phases 2–3 application code, CI, Docker, and this audit exist as **uncommitted** files on top of that commit. The audit inspected the working tree, not git HEAD alone.

AUTHORITATIVE SPEC:  
`Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` — **not present in this workspace**. Phase 0–1 documents claim they were derived from PDF v1.0 (August 2026). The binary was searched under the workspace and the parent Desktop folder and was not found.

========================================================

## EXECUTIVE SUMMARY

OVERALL RESULT:  
PASS

OVERALL SCORE:  
91/100

READY FOR PHASE 4:  
YES

Phases 0–3 are implemented in the working tree as documentation (0–1) plus a real engineering foundation and a mocked conversation UX (2–3). Validation commands for format, lint, typecheck, unit tests, Playwright Chromium E2E, production build, `next start`, API `/health`, npm/pip audits, and Docker Compose **config** all passed after audit fixes.

This is **not** a production voice assistant. Real STT, TTS, audio streaming, barge-in, orchestration, RAG, and tools are not implemented and are not claimed as complete.

========================================================

## PHASE 0

STATUS:  
VERIFIED PASS

SCORE:  
90/100

REQUIREMENTS VERIFIED:

- Product purpose, users, use cases, MVP, deferred features, and out-of-scope items are in `docs/product.md`.
- Success criteria, source strategy, security/privacy/retention assumptions, and unassigned ownership are documented.
- Architecture constraints are in `docs/ARCHITECTURE.md` (canonical `docs/architecture.md` on Windows).
- Risks, PDF-vs-docs conflicts (C-01–C-07), and assumptions are in `docs/risk-register.md`.
- MVP does **not** require long-term personal memory; architecture and product both exclude it.
- RAG is scheduled later (Phase 6); architecture does not claim it is implemented.
- ADRs 0001–0007 exist.

ISSUES:

- The PDF specification file is not in the repository (MEDIUM).
- Named owners remain UNASSIGNED (documented; expected until Cyber Florida names people).
- `docs/GAP_ANALYSIS.md` and `docs/REPOSITORY_ASSESSMENT.md` remain historical Phase 0 snapshots below status banners.
- Dedicated “Phase 0 completion report” files were not found; README / ROADMAP / product exit sections serve that role.

FIXES:

- Status banners on `docs/product.md`, `docs/SECURITY.md`, `docs/GAP_ANALYSIS.md`, `docs/REPOSITORY_ASSESSMENT.md`.
- Corrected product success-criteria wording so it does not say there is “no product” after Phase 3.
- Noted the implemented `packages/pixel` layout in architecture.

EXIT CRITERIA:  
PASS

========================================================

## PHASE 1

STATUS:  
VERIFIED PASS

SCORE:  
94/100

POLICY COVERAGE:

`docs/policies.md` v1.1.0 (`pixel-behavior`) plus `safety-rules.md`, `escalation-matrix.md`, and `tool-confirmation-policy.md` cover:

- Pixel identity and AI disclosure
- Voice and screen style, answer length
- Source grounding, uncertainty, freshness
- Cybersecurity, phishing/scam, defensive incident guidance
- Sensitive information, follow-ups, context, unsupported requests
- Escalation, tool confirmation, prompt injection, provider/system failure

Policies are **not loaded by runtime code** (no orchestrator yet). That is correct for Phase 1.

CONVERSATION EXAMPLES:

`docs/conversation-examples.md` contains **EX-001 through EX-102** (102 dialogues). This is not a file-count trick; headings were inspected.

Coverage includes normal Cyber Florida questions, program discovery, follow-ups, education, scam analysis, incident guidance, uncertainty, missing sources, ambiguity, prompt injection, secret requests, unsupported requests, tool confirmation, and failure cases. Examples are not only happy-path repeats.

Machine-readable fixtures: `evals/policy/cases.jsonl` (83 lines) and `evals/safety/cases.jsonl` (19 lines). Unscored, as expected.

SAFETY COVERAGE:

Numbered SHALL rules, escalation categories E-01–E-10, and tool confirmation classes exist. Mock UX now refuses dump-system-prompt / ignore-previous / api-keys shaped inputs without leaking instructions.

ISSUES:

- Mock Cyber Florida answers in Phase 3 are canned and labeled mock; production policy still requires RAG for org facts (intentional prototype gap, not a silent policy override).
- Policy owner approval remains UNASSIGNED.
- No standalone Phase 1 completion report file.

FIXES:

- Mock provider refusal path and unit test for injection/secret-shaped prompts.

EXIT CRITERIA:  
PASS

========================================================

## PHASE 2

STATUS:  
VERIFIED PASS

SCORE:  
90/100

REPOSITORY:

```text
CURRENT BRANCH:     main
CURRENT COMMIT:     7178fc17003c2410b1eb468e0ece491739924157
WORKING TREE:       dirty (Phases 2–3 + audit uncommitted)
FRONTEND:           Next.js 16.3.1, React 19, TypeScript
BACKEND:            FastAPI (pixel_api)
PACKAGE MANAGER:    npm workspaces + pip/pyproject (editable pixel)
TEST FRAMEWORKS:    Vitest, Playwright, pytest
TYPE-CHECKING:      tsc --noEmit, pyright (basic)
LINTING:            ESLint (eslint-config-next), Ruff
FORMATTING:         Prettier, Ruff format
CI/CD:              .github/workflows/ci.yml (api + web jobs)
DOCKER:             infra/docker-compose.yml, api.Dockerfile, web.Dockerfile
DATABASE:           Postgres/pgvector service in Compose; no Phase 6 tables
ENV:                .env.example plus development/staging/production examples
```

Structure matches ADR-0001 (modular monolith): `apps/web`, `apps/api`, `apps/worker`, `packages/pixel` (ai/voice/knowledge/tools/security/observability/shared modules), `infra/`, `evals/`, `docs/`. Separate publishable packages per folder were not required.

FRONTEND FOUNDATION:

TypeScript, Next scripts, Prettier, ESLint, Vitest, production build, and public-env secret-shape guard all verified. No `any` / `@ts-ignore` / `@ts-nocheck` / `eslint-disable` found in application TypeScript. `output: "standalone"` is now **opt-in** via `OUTPUT_STANDALONE=1` so local `next start` works; Docker still sets that env.

BACKEND FOUNDATION:

FastAPI app with settings, CORS allowlist (rejects `*`), health/ready, admin fail-closed 403, structured errors, correlation IDs. Live `/health` returned 200. `/ready` returned `database: not_configured` without Compose Postgres (expected). Production settings reject mock providers. Worker is an idle stub (Phase 6).

ENVIRONMENT:

`.env` is gitignored. No real `.env` committed. Example files use empty `OPENAI_API_KEY=` and local `pixel_dev_only` Compose password, clearly labeled non-production. `sk-test` appears only as a **rejection fixture** in `env.test.ts`.

CI:

Workflow commands match real npm/Python scripts: ruff format/check, pyright, pytest, pip-audit, Prettier, ESLint, tsc, Vitest, Next build, Playwright, npm audit. CI is not a no-op.

TESTING:

Meaningful assertions on health, CORS, admin 403, secret leakage, public env, provider protocols, state machine, mock provider, and UI labels.

SECURITY:

No committed live secrets found. CORS origins are explicit. Admin disabled. Health does not echo `DATABASE_URL`. React renders transcript as text (no `dangerouslySetInnerHTML`).

ISSUES:

- `docker compose up` **not verified** (Docker Desktop daemon not running).
- Local Python is 3.14.2; CI and `requires-python` are 3.12.
- Phases 2–3 are not in git HEAD.
- `CORSMiddleware` `allow_headers=["*"]` allows any request header on allowlisted origins (not origin wildcard).
- `docs/testing/README.md` was stale (fixed).

FIXES:

- Standalone output opt-in + Dockerfile `OUTPUT_STANDALONE=1`.
- `.gitignore` for Next-generated `AGENTS.md` / `CLAUDE.md`.
- Architecture / testing / ADR index drift notes.

EXIT CRITERIA:  
PASS

========================================================

## PHASE 3

STATUS:  
VERIFIED PASS

SCORE:  
91/100

STATE MACHINE:

Single reducer in `apps/web/src/conversation/state-machine.ts`. User-visible states: `idle`, `listening`, `processing`, `speaking`, `error`, `permission_denied`. `cancelled` is a short announcement, then idle. Listening and speaking cannot both be true. Invalid events are ignored.

MICROPHONE UX:

Permission unknown / granted / denied / unavailable. Denied keeps text usable. Phase 3 does **not** transcribe; Stop sends a selected sample utterance. Documented in UI banner and `docs/conversation-ux.md`.

TEXT INPUT:

Labeled textarea, Enter to send, Shift+Enter newline, empty submit disabled, busy disables composer, focus returns after idle. Playwright: type → send → mock reply.

TRANSCRIPT:

Ordered list, You vs Pixel roles, text wrapping via CSS, mock source cards labeled “Mock source — not live RAG”.

CONTROLS:

Stop, Mute, Cancel, Clear (modal confirm) have accessible names. Phase 3 behavior is state-level / simulated speech duration, not live TTS cancel.

SOURCE CARDS:

Title, description, name, URL. Non-allowlisted hrefs render as blocked text, not `<a>`. Allowlist: `https://cyberflorida.org` and `www.cyberflorida.org` only.

MOCK PROVIDER:

Isolated in `mock-provider.ts`. Deterministic phrases including simulated failures. UI does not hardcode answers.

ERROR RECOVERY:

`simulate network error` → error panel → Try again → idle (E2E). Copy has no stack traces.

RESPONSIVE DESIGN:

CSS stacks composer and full-width controls at `max-width: 640px`. **Physical tablet/mobile screenshot pass: NOT VERIFIED** (Playwright uses Desktop Chrome only).

ACCESSIBILITY:

Visible `:focus-visible` outlines, labeled controls, live state text (not color alone), transcript region, dialog labelled. No axe-core suite. Full human keyboard tour not recorded; unit/E2E cover labels and core clicks.

TESTING:

31 Vitest tests, 3 Playwright tests after audit. Weak `expect(true).toBe(true)` patterns were not found.

ISSUES:

- No automated axe scan; no mobile Playwright project.
- E2E does not cover Clear / Cancel / Mute / permission-denied click path.
- Listening path is a sample phrase, not STT (correct for Phase 3; must not be mistaken for Phase 4).

FIXES:

- Href allowlist + tests.
- Accessible names on source/action links.
- Removed noisy “No source cards for this turn” on every Pixel reply.
- Mock injection refusals.

EXIT CRITERIA:  
PASS

========================================================

## ISSUES FOUND

CRITICAL:  
- None.

HIGH:  
- Source/action URLs were previously rendered without an allowlist (could navigate to arbitrary `javascript:` / off-site hrefs if mock data changed). **Fixed.**
- `next start` failed when `output: "standalone"` was always on (missing `server.js` in the default Next layout). **Fixed.**

MEDIUM:  
- Authoritative PDF not in the workspace.
- Phases 2–3 exist only in the working tree, not commit `7178fc1`.
- Docker Compose **up** not verified (daemon down). Compose **config** verified.
- Local Python 3.14 vs CI 3.12.
- Historical GAP/REPOSITORY tables can still be misread if banners are skipped.
- No axe-core accessibility suite; Playwright is desktop Chromium only.
- CORS `allow_headers=["*"]` on an origin allowlist.
- Mock org-fact answers vs production grounding policy (labeled mock; expected until Phase 6).

LOW:  
- npm `Unknown env config "devdir"` warning on this machine.
- Starlette/httpx TestClient deprecation warning.
- Combined `packages/pixel` vs the originally sketched per-folder packages (documented, ADR-0001).
- No dedicated Phase 0–3 “completion report” files (README/ROADMAP used instead).

========================================================

## ISSUES FIXED:

- Allowlisted Cyber Florida HTTPS links only; blocked hrefs are not clickable.
- Next standalone output is opt-in; Docker still builds standalone.
- Mock provider refuses dump-system-prompt / ignore-previous / api-keys shaped prompts.
- Source and action links have accessible names including “opens in a new tab”.
- Blocked action chips use dashed styling.
- Removed per-turn “No source cards” clutter.
- Documentation status banners and testing/ADR/product/architecture drift corrections.
- `.gitignore` for Next-generated agent instruction files.

========================================================

## FILES MODIFIED:

Audit-time changes (plus this report):

- `apps/web/next.config.ts`
- `apps/web/src/conversation/allowlist.ts` (new)
- `apps/web/src/conversation/allowlist.test.ts` (new)
- `apps/web/src/conversation/mock-provider.ts`
- `apps/web/src/conversation/mock-provider.test.ts`
- `apps/web/src/components/SourceCard.tsx`
- `apps/web/src/components/RecommendedAction.tsx`
- `apps/web/src/components/ConversationTurn.tsx`
- `apps/web/src/components/conversation-ui.test.tsx`
- `apps/web/src/app/globals.css`
- `infra/web.Dockerfile`
- `.gitignore`
- `docs/product.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/GAP_ANALYSIS.md`
- `docs/REPOSITORY_ASSESSMENT.md`
- `docs/testing/README.md`
- `docs/decisions/README.md`
- `docs/audits/phases-0-3-engineering-audit.md` (this file)

========================================================

## TESTS RUN:

Command:  
`npm run web:format:check`  
Result: PASS

Command:  
`npm run web:lint`  
Result: PASS

Command:  
`npm run web:typecheck`  
Result: PASS

Command:  
`npm run web:test`  
Result: PASS (31 passed / 7 files)

Command:  
`npm run web:build`  
Result: PASS

Command:  
`npm run web:e2e`  
Result: PASS (3 passed, Chromium)

Command:  
`npm run web:start` then `GET http://127.0.0.1:3000/`  
Result: PASS (HTTP 200; page includes mocked-prototype copy)

Command:  
`python -m ruff format --check apps/api apps/worker packages/pixel`  
Result: PASS

Command:  
`python -m ruff check apps/api apps/worker packages/pixel`  
Result: PASS

Command:  
`python -m pyright`  
Result: PASS (0 errors)

Command:  
`python -m pytest`  
Result: PASS (13 passed, 1 Starlette deprecation warning)

Command:  
`python -m uvicorn pixel_api.main:app --host 127.0.0.1 --port 8000` then `GET /health` and `GET /ready`  
Result: PASS (`/health` 200 `ok`; `/ready` 200 `database: not_configured`)

Command:  
`npm audit --audit-level=high`  
Result: PASS (0 vulnerabilities)

Command:  
`python -m pip_audit`  
Result: PASS (no known vulnerabilities; local package `pixel` skipped as not on PyPI)

Command:  
`docker compose -f infra/docker-compose.yml config`  
Result: PASS

Command:  
`docker compose -f infra/docker-compose.yml up`  
Result: NOT VERIFIED  
REASON: Docker client is installed; Docker Desktop daemon was not running (`docker info` failed).

Command:  
Physical tablet/mobile layout inspection  
Result: NOT VERIFIED  
REASON: No device/emulated viewport pass beyond CSS media queries and desktop Playwright.

Command:  
axe-core / dedicated a11y scanner  
Result: NOT VERIFIED  
REASON: No axe script is configured. Labels and focus styles were inspected in source and unit tests.

Command:  
Read `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf`  
Result: NOT VERIFIED  
REASON: File is not in the workspace.

========================================================

## TEST RESULTS:

Passed:  
Web format, lint, typecheck, 31 Vitest, Next build, 3 Playwright, `next start` HTTP 200, Ruff format/check, pyright, 13 pytest, API health/ready, npm audit, pip-audit, Compose config.

Failed:  
None of the executed checks.

Skipped:  
None of the configured suites were skipped.

Not Verified:  
Docker Compose up; PDF binary; physical responsive devices; axe-core; full human keyboard tour.

========================================================

## SECURITY REVIEW:

Result:  
PASS

Findings:

- No live API keys, tokens, or private keys committed.
- `.env` ignored; examples leave provider keys empty.
- CORS origins cannot be `*`.
- Admin routes 403 until `ADMIN_ENABLED` and real auth exist.
- Production settings reject mock LLM/STT/TTS/embedding providers.
- Browser env rejects secret-shaped `NEXT_PUBLIC_*` names.
- Transcript is text nodes, not HTML injection.
- Phase 3 hrefs are now host-allowlisted HTTPS only.
- Compose `pixel_dev_only` is a local placeholder, not a production secret.
- Credential rotation is **not** indicated (no live secret was found in git).

========================================================

## ACCESSIBILITY REVIEW:

Result:  
PASS (with remaining MEDIUM gaps)

Findings:

- Icon/text controls have accessible names.
- State is announced as text via `role="status"`.
- Composer field is labeled; Send is a real submit button.
- Clear uses a native `dialog` with a title.
- Focus outlines are explicit.
- Missing: axe suite, mobile viewport E2E, recorded keyboard-only tour.
- Source/action links now include “opens in a new tab”.

========================================================

## ARCHITECTURE REVIEW:

Result:  
PASS

Findings:

- Web client, API, worker stub, and provider protocols are separated.
- No vendor SDKs in the UI.
- Conversation mock is isolated from components.
- Knowledge/tools packages are explicit Phase 6/7 placeholders.
- Intended API (`/v1/sessions`, WebSocket realtime) is **not** built; only `/health`, `/ready`, fail-closed `/admin/*`. That is correct for Phases 2–3.
- Folder sketch in architecture used many `packages/*` directories; implementation uses one `pixel` package with modules (ADR-0001). Documented during this audit.

========================================================

## FALSE COMPLETION FINDINGS:

- No false claim that Phase 4 (real STT/TTS/streaming/barge-in) is complete.
- UI banner and README state replies are mocked.
- `docs/ROADMAP.md` already said Phase 4 may start only on explicit instruction and that live STT/TTS/RAG must not be assumed.
- Git HEAD does **not** contain Phases 2–3; calling those phases “complete” is true of the working tree, not of the last commit.

========================================================

## PLACEHOLDER / TODO FINDINGS:

- No `TODO` / `FIXME` / `HACK` in application TypeScript/Python.
- `packages/pixel` knowledge/tools modules are labeled Phase 6/7 placeholders (correct).
- Worker prints idle and registers no jobs (correct).
- Input `placeholder=` on the composer is UI copy, not a stub.
- Eval datasets are unscored fixtures.

========================================================

## REMAINING TECHNICAL DEBT:

- Commit (and optionally push) Phases 2–3 so git matches the audited tree.
- Align local Python with 3.12 or document 3.14 as unsupported-but-working.
- Add axe and a mobile Playwright project before calling WCAG 2.2 AA done.
- Tighten CORS allowed headers when real APIs exist.
- Replace mock org answers with RAG in Phase 6; do not promote canned facts.
- Postgres session schema still belongs to later phases (ADR-0005).

========================================================

## DEFERRED ISSUES:

- Real STT/TTS, streaming, barge-in (Phase 4).
- Orchestrator and policy enforcement in code (Phase 5).
- RAG / pgvector knowledge tables (Phase 6).
- Tools and confirmation UX beyond mock links (Phase 7).
- Authn/SSO and production hardening (Phase 8+).
- Docker daemon / full-stack Compose up on this machine.
- Owner assignment and PDF check-in.
- Feedback capability (MVP later, not Phase 3).

========================================================

## REGRESSION RISKS:

- Re-enabling unconditional `output: "standalone"` will break `npm run web:start` again unless the Docker copy layout is used.
- Expanding mock `href` values off `cyberflorida.org` will show blocked chips instead of links (intentional).
- Uncommitted work can be lost or diverge from GitHub if not committed before Phase 4.
- Listening still sends a sample phrase; wiring real STT without replacing that path would silently ship fake transcripts.

========================================================

## FINAL VERDICT

PHASE 0:  
PASS

PHASE 1:  
PASS

PHASE 2:  
PASS

PHASE 3:  
PASS

OVERALL:  
PASS

READY FOR PHASE 4:  
YES

REASON:  
Critical and high findings are resolved. Required lint, types, tests, and frontend build pass. Phase 0–1 documentation is real and internally consistent. Phase 2 foundation starts and is tested. Phase 3 mocked conversation UX works, including text, mock listen/stop, source cards, and error recovery, and it does not claim live voice. Remaining items are medium/low process, coverage, or later-phase work.

========================================================

## RECOMMENDED NEXT ACTION:

Wait for the explicit instruction **Proceed to Phase 4.**

Before that work, commit the uncommitted Phase 2–3 tree so the voice loop is not built on files that exist only locally. Do not start real STT/TTS until that instruction is given.
