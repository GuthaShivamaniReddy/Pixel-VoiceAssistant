# Pixel security review (Phase 8)

**Date:** 2026-08-17  
**Scope:** Running Pixel API, web client, orchestrator, RAG, tools, CI, and documentation. Phase 9 visual polish is out of scope.

## SCOPE

Harden trust boundaries from microphone to logs. Architectural controls over prompt-only rules.

## THREAT MODEL SUMMARY

See `docs/security/threat-model.md`. Highest-value assets: provider keys, admin token, DB URL, session IDs, knowledge integrity, audio/transcripts.

## AUTHENTICATION REVIEW

Public Q&A is anonymous with UUID sessions. There is no user password table. Admin HTTP requires `ADMIN_ENABLED=true` **and** `ADMIN_TOKEN`. Empty token keeps admin disabled even if the flag is true. Production rejects `ADMIN_ENABLED` with a short token.

## AUTHORIZATION REVIEW

`AuthContext` is assigned by the API as `public`. Tools and retrieval do not read roles from the client, model, or documents. Direct `/admin/*` calls without a valid bearer token are 401/403.

## PROMPT-INJECTION REVIEW

User injection is classified and skipped around the model for known patterns. Output validation blocks secret-shaped and policy-leak replies. Retrieved HTML is evidence only. Tests cover user, multi-turn, and poison-document cases. This is not a proof that a live vendor model can never be socially engineered; core privileges remain impossible without server authorization.

## RAG SECURITY

Public runtime retrieval is `access_class=public`. Caller-supplied `access_class` is ignored. Inactive sources are excluded. Fetch is allowlisted HTTPS without redirects.

## TOOL SECURITY

Four named tools. Unknown names fail. URLs must be registered `https://cyberflorida.org` canonical pages. Private hosts and unsafe schemes are rejected. Kill switches: `TOOLS_ENABLED`, `DISABLED_TOOLS`, `SIDE_EFFECTING_TOOLS_ENABLED`.

## SECRET MANAGEMENT

No live provider secrets in git or `NEXT_PUBLIC_*`. `.env` gitignored. Examples use placeholders / local-only `pixel_dev_only`. Scan test fails on live-key markers. Rotation: `docs/runbooks/secret-rotation.md`.

## RATE LIMITING

In-process per IP (and per session for turns). Defaults: 30 session creates/min, 120 turns/min/IP, 60 turns/min/session, 30 WS connects/min, 20 admin/min. HTTP 429 + `Retry-After`. Not distributed.

## INPUT VALIDATION

JSON body cap (`MAX_REQUEST_BYTES`, default 64KiB). User text 4000 chars (orchestrator) / 8000 pydantic ceiling. WS control 8KiB. Audio 1MiB. Session/turn IDs length-limited. Tool arguments schema-validated.

## HEADERS / CORS

API: CSP `default-src 'none'`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, HSTS in production. CORS explicit origins, credentials off, no `*`. Web: CSP allowing self + configured API `connect-src`, `media-src blob:` for playback, `microphone=(self)`. Development CSP may include `unsafe-eval` for Next.js; production script-src is `'self'`. Style-src allows `'unsafe-inline'` because Next injects CSS.

## LOGGING

Redacting filter on `pixel*` loggers. Turn logs use session/turn/intent/status, not transcripts. Correlation IDs must be UUIDs. Admin audit: actor/timestamp/action/target/result/correlation_id.

## PRIVACY

Raw audio is not stored. Transcripts live in the in-memory session until TTL or Clear. Retention periods for production logs are UNASSIGNED (institutional). See `docs/security/data-retention.md`.

## DEPENDENCIES

CI: `pip-audit`, `npm audit --audit-level=high`. Phase 8 does not blindly bump every package.

## INCIDENT RESPONSE

`docs/runbooks/security-incident.md`, `secret-rotation.md`. Kill switches are environment flags (process restart required with current Settings load). Bad source: `deactivate_source`.

## FINDINGS

Recorded in the Phase 8 completion report. CRITICAL must be zero for PASS.

## REMEDIATIONS

Rate limits, headers, CSP, redaction, admin token, request size, kill switches, correlation-id sanitization, retrieval access_class pin, expanded injection tests, secret scan, runbooks.

## DEFERRED ISSUES

- USF SSO / real staff roles
- Redis/distributed rate limits
- Separate Postgres runtime vs migration roles
- HTTP admin ingest API
- Institutional retention periods and legal privacy wording
- Live-model red-team scoring
- Pin GitHub Actions by SHA
