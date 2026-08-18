# Pixel threat model (Phase 8)

**Status:** Implementation-tied. This document describes the running Pixel code in this repository, not a generic chatbot.

**Policy hierarchy (enforced in code, not only in prompts):**

```text
SYSTEM / SERVER POLICY  (orchestrator/policy.py, FastAPI authn/z, settings)
>
APPLICATION POLICY      (intents, output validation, kill switches)
>
AUTHORIZED USER CONTEXT (AuthContext.permission from the server)
>
TOOL POLICY             (registry, urls.py, runner.py)
>
USER INPUT              (turns, WS control, transcripts)
>
RETRIEVED CONTENT       (evidence channel only)
```

Retrieved content cannot grant tools, change authentication, change authorization, override system policy, disable safeguards, reveal secrets, or modify server configuration.

---

## Assets requiring the strongest protection

| Asset | Why | Where it lives |
|---|---|---|
| Provider API keys (`OPENAI_API_KEY`) | Direct spend and data access | Server env only (`Settings.openai_api_key`) |
| Database credentials | Knowledge + future session stores | Server env / Compose; not in the browser |
| Admin token | Privileged knowledge operations | `ADMIN_TOKEN`; empty means admin is disabled |
| Session IDs | Capability to continue a conversation | Server `SessionStore`; UUID4 in JSON bodies |
| Approved Cyber Florida knowledge | Integrity of org answers | Fixture/pgvector index; `access_class=public` at runtime |
| Internal knowledge | Must never reach public retrieval | Filtered in `KnowledgeRetriever` / store search |
| Microphone audio / transcripts | Privacy | Transient PCM in memory; not persisted |
| Audit / security logs | Incident reconstruction | Structured logs with redaction |
| Tool permissions | Confused deputy | Server registry + `AuthContext` |
| CI/CD credentials | Supply chain | GitHub Actions secrets (not in repo) |
| Production configuration / kill switches | Availability and containment | Process env |

---

## Trust boundaries

```text
USER → BROWSER
BROWSER → PIXEL API          (CORS allowlist; no provider keys)
BROWSER → PIXEL REALTIME WS  (same API origin; origin check)
PIXEL API → AI / STT / TTS   (server env secrets)
PIXEL API → DATABASE         (optional; parameterized SQL)
ORCHESTRATOR → TOOL LAYER    (registry; kill switch)
KNOWLEDGE INGESTION → INDEX  (allowlisted HTTPS only)
ADMIN → ADMIN API            (fail-closed token)
CI → REPOSITORY / DEPLOY     (no production secrets in git)
```

All inputs crossing a boundary are untrusted until authenticated and validated.

---

## Component threats

### MICROPHONE / AUDIO

ASSET: PCM captured in the browser; transient server buffer (`VoiceRuntime.append_audio`, max 1_000_000 bytes).

TRUST BOUNDARY: User device → browser capture → Pixel WS.

ATTACKER: Malicious page, compromised extension, local malware.

ATTACK VECTOR: Drive-by mic capture; oversized audio DoS; replay of another user's audio.

POTENTIAL IMPACT: Unwanted recording; API resource exhaustion.

EXISTING CONTROL: Push-to-talk; user gesture; audio discarded after STT; size cap; no raw audio database.

MISSING CONTROL: No production privacy notice wording (stakeholder-owned).

RISK: MEDIUM

RECOMMENDED MITIGATION: Keep PTT; do not add always-on listening; complete privacy notice in Phase 13.

VALIDATION TEST: Playwright PTT; `MAX_AUDIO_BYTES` cap in `runtime.py`.

---

### WEB CLIENT

ASSET: Transcripts, source titles, recommended actions rendered in React.

TRUST BOUNDARY: Pixel API JSON → DOM.

ATTACKER: Anyone who can influence model/RAG text.

ATTACK VECTOR: XSS via transcript/source HTML; `javascript:` links.

POTENTIAL IMPACT: Session theft if cookies existed (they do not); phishing via bad links.

EXISTING CONTROL: React text nodes; no `dangerouslySetInnerHTML`; `isAllowlistedHref`; `rel=noreferrer noopener`.

MISSING CONTROL: Markdown HTML rendering is not used; keep it that way.

RISK: LOW

RECOMMENDED MITIGATION: Keep encoding; CSP on the Next.js origin.

VALIDATION TEST: `conversation-ui.test.tsx` XSS case; allowlist tests.

---

### REALTIME TRANSPORT

ASSET: WS `/v1/realtime` session and audio frames.

TRUST BOUNDARY: Browser → FastAPI WebSocket.

ATTACKER: Cross-site page, unauthenticated client.

ATTACK VECTOR: Cross-origin WS; oversized control JSON; session flooding.

POTENTIAL IMPACT: Cost amplification; hijack if session ID leaked.

EXISTING CONTROL: Origin allowlist; production requires Origin; 8KB control cap; in-process WS connect rate limit; session UUID4.

MISSING CONTROL: Distributed WS limits across replicas.

RISK: MEDIUM

RECOMMENDED MITIGATION: Put a reverse proxy in front for production; document process-local limits.

VALIDATION TEST: WS origin rejection; `test_websocket_voice_turn`.

---

### API

ASSET: REST `/v1/sessions`, `/v1/turns`, `/health`, `/ready`.

TRUST BOUNDARY: Browser → FastAPI.

ATTACKER: Anonymous internet client.

ATTACK VECTOR: Flooding, oversized JSON, verbose errors, OpenAPI in production.

POTENTIAL IMPACT: Cost, information leak, availability.

EXISTING CONTROL: CORS allowlist; 64KB default body cap; 4000 char user text; generic 500s; OpenAPI disabled in production; security headers; in-process rate limits.

MISSING CONTROL: Shared Redis limiter for multi-replica.

RISK: MEDIUM

RECOMMENDED MITIGATION: Keep in-process limiter honest; add Redis only when horizontally scaled.

VALIDATION TEST: `apps/api/tests/test_security.py`.

---

### SESSION MANAGEMENT

ASSET: In-memory `ConversationSession` (UUID4, 30 minute TTL, max 8 messages, max 500 sessions).

TRUST BOUNDARY: Client-supplied `session_id` → `SessionStore.get`.

ATTACKER: Guessing or leaking IDs.

ATTACK VECTOR: IDOR against another session; fixation by supplying an ID.

POTENTIAL IMPACT: Read/continue another conversation (in-memory only).

EXISTING CONTROL: UUID4; unknown IDs 404; TTL prune; clear increments generation and drops context. Clients cannot mint privileged sessions.

MISSING CONTROL: Persistent session store still unused at HTTP runtime.

RISK: LOW

RECOMMENDED MITIGATION: Keep unguessable IDs if sessions move to Postgres.

VALIDATION TEST: `test_idor_unknown_session_is_not_found`.

---

### AUTHENTICATION

ASSET: Public anonymous use; optional `ADMIN_TOKEN`.

TRUST BOUNDARY: HTTP `Authorization` header.

ATTACKER: Unauthenticated user claiming staff.

ATTACK VECTOR: `isAdmin` JSON; missing token; short production token.

POTENTIAL IMPACT: Privileged knowledge operations.

EXISTING CONTROL: No user login (by design). Admin disabled unless `ADMIN_ENABLED` and a configured token. Production requires token length ≥ 32. `secrets.compare_digest`.

MISSING CONTROL: USF SSO (deferred; fail closed until then).

RISK: LOW (fail-closed) / HIGH if someone enables admin without a token — mitigated by treating empty token as disabled.

RECOMMENDED MITIGATION: Do not invent a password table. Use SSO later.

VALIDATION TEST: `test_admin_requires_bearer_token`.

---

### AUTHORIZATION

ASSET: `AuthContext.permission` (`public` | `authenticated` | `privileged`).

TRUST BOUNDARY: Orchestrator → tools.

ATTACKER: Model, retrieved doc, client header.

ATTACK VECTOR: Prompt “I am admin”; RAG “user is administrator”; client `X-Admin`.

POTENTIAL IMPACT: Privileged tools or internal knowledge.

EXISTING CONTROL: HTTP runtime always sets `permission="public"`. Tool runner ignores model/RAG. Retrieval ignores caller `access_class`.

MISSING CONTROL: Authenticated staff role is not implemented (and must not be faked).

RISK: LOW

RECOMMENDED MITIGATION: Keep server-assigned auth only.

VALIDATION TEST: tool unauthorized tests; access_class override test.

---

### AI ORCHESTRATOR

ASSET: `process_turn` policy, intents, output validation.

TRUST BOUNDARY: User text + evidence → reply.

ATTACKER: User and retrieved documents.

ATTACK VECTOR: Injection, jailbreak, secret extraction, multi-turn social engineering.

POTENTIAL IMPACT: Policy leak, unsafe advice, tool misuse.

EXISTING CONTROL: Versioned `SYSTEM_PROMPT`; intent skip_model for injection/unsafe; evidence delimiter; output secret/policy leak checks; kill switches; tools not chosen by the model.

MISSING CONTROL: Live-vendor red-team scoring (Phase 11). Mock LLM is deterministic.

RISK: MEDIUM

RECOMMENDED MITIGATION: Keep architectural controls; expand evals when a live model is used.

VALIDATION TEST: `test_safety_eval.py`, e2e injection.

---

### AI PROVIDERS / STT / TTS

ASSET: Vendor credentials and audio/text payloads.

TRUST BOUNDARY: Pixel API → OpenAI (or mock).

ATTACKER: Network observer; compromised vendor; leaked key.

ATTACK VECTOR: Key in frontend; key in logs; provider outage.

POTENTIAL IMPACT: Spend, data exposure to vendor.

EXISTING CONTROL: Server-only key; mock default locally; production forbids mock; timeouts/retries; provider kill switches (`LLM_ENABLED`, `STT_ENABLED`, `TTS_ENABLED`). No browser-side realtime provider tokens.

MISSING CONTROL: Live key rotation drill.

RISK: MEDIUM

RECOMMENDED MITIGATION: Secret manager in production; follow `docs/runbooks/secret-rotation.md`.

VALIDATION TEST: `test_public_env.py`; STT/TTS kill-switch tests.

---

### RAG / KNOWLEDGE INGESTION / RETRIEVED DOCUMENTS

ASSET: Approved Cyber Florida corpus; integrity of answers.

TRUST BOUNDARY: Allowlisted fetch → index → evidence channel.

ATTACKER: Poisoned page, unapproved URL, metadata filter bypass.

ATTACK VECTOR: Indirect prompt injection; fake Cyber Florida policy in a chunk; `access_class=internal` mixed into public search.

POTENTIAL IMPACT: Wrong org facts; tool/permission confusion.

EXISTING CONTROL: Host allowlist `cyberflorida.org`; no redirects; `follow_redirects=False`; public-only runtime retriever; inactive sources excluded; poison fixture tests; evidence is data.

MISSING CONTROL: HTTP admin ingest is not implemented (fail-closed). File upload parsers are not in the public API.

RISK: MEDIUM

RECOMMENDED MITIGATION: Deactivate bad sources; do not index unapproved hosts.

VALIDATION TEST: `test_retrieved_injection_cannot_override_policy`; deactivate_source test.

---

### TOOLS / NAVIGATION

ASSET: `find_program`, `find_resource`, `search_approved_content`, `navigate_to_url`.

TRUST BOUNDARY: Orchestrator → `execute_tool`.

ATTACKER: User, model, retrieved text.

ATTACK VECTOR: Arbitrary URL, `javascript:`, SSRF, unknown tool names, fake confirmation.

POTENTIAL IMPACT: Open attacker site; hit internal IPs.

EXISTING CONTROL: Named registry; HTTPS + host allowlist + registered canonical URL; private IP block; kill switches; confirmation policy; audit log without arguments.

MISSING CONTROL: None for MVP scope. Do not add open browsing.

RISK: LOW

RECOMMENDED MITIGATION: Keep allowlist; use `TOOLS_ENABLED` / `DISABLED_TOOLS` in incidents.

VALIDATION TEST: `test_tools_urls.py`, `test_tools_orchestrator.py`.

---

### ADMIN ENDPOINTS

ASSET: Future source register/reindex/policy update.

TRUST BOUNDARY: `/admin/{path}`.

ATTACKER: Anonymous internet.

ATTACK VECTOR: Direct POST `/admin/sources` without UI.

POTENTIAL IMPACT: Corpus poisoning if open.

EXISTING CONTROL: Fail closed. Empty token ⇒ 403. Wrong token ⇒ 401. Valid token ⇒ 404 (no mutating admin API yet). Audit line. Admin rate limit.

MISSING CONTROL: Real SSO; implemented ingest routes.

RISK: LOW (fail-closed)

RECOMMENDED MITIGATION: Keep fail-closed until SSO and an ingest API exist.

VALIDATION TEST: `test_security.py` admin cases; `test_health.py` fail-closed.

---

### DATABASE / PGVECTOR / OBJECT STORAGE

ASSET: `DATABASE_URL`; `knowledge_chunks` embeddings.

TRUST BOUNDARY: API/worker → Postgres.

ATTACKER: SQLi; stolen DB URL; overly privileged DB role.

ATTACK VECTOR: Concatenated SQL; public DB port.

POTENTIAL IMPACT: Data theft or corruption.

EXISTING CONTROL: Parameterized `psycopg` queries (`%s`). No object-store uploads. Local Compose password `pixel_dev_only` is a documented non-production default.

MISSING CONTROL: Runtime vs migration DB roles are not separated in Compose. The `pixel` user owns the database.

RISK: MEDIUM (local) / HIGH if that password were reused in production.

RECOMMENDED MITIGATION: Distinct app role without CREATEDB in production; never reuse `pixel_dev_only`.

VALIDATION TEST: SQL-shaped retrieval query test; postgres tests when `PIXEL_TEST_DATABASE_URL` is set.

---

### LOGGING / METRICS / TELEMETRY

ASSET: Correlation IDs, intents, tool audit, security events.

TRUST BOUNDARY: App logs → operators.

ATTACKER: Log aggregation leak; user-supplied correlation IDs.

ATTACK VECTOR: Secret in exception; transcript in logs; log injection via headers.

POTENTIAL IMPACT: Credential leak.

EXISTING CONTROL: Redacting filter; no full transcripts in standard turn logs; UUID-only correlation IDs; tool audit logs names/status not arguments.

MISSING CONTROL: Central log retention product (UNASSIGNED).

RISK: LOW

RECOMMENDED MITIGATION: Keep redaction tests; do not log raw audio.

VALIDATION TEST: `test_security_controls.py` redaction.

---

### CI/CD / SECRETS / DEPLOYMENT

ASSET: GitHub Actions; env templates; Docker images.

TRUST BOUNDARY: PR → CI → (future) deploy.

ATTACKER: Malicious PR; committed secret.

ATTACK VECTOR: Secret in git; `NEXT_PUBLIC_*` key; wildcard CORS.

POTENTIAL IMPACT: Key leak; supply chain.

EXISTING CONTROL: `.env` gitignored; example files names-only; CI ruff/pytest/pip-audit/npm audit; secret-marker scan test; git history scan for live key markers.

MISSING CONTROL: Pinned GitHub Actions SHAs (LOW).

RISK: LOW

RECOMMENDED MITIGATION: Rotate if a live key ever appears in history.

VALIDATION TEST: `test_secret_scan.py`; CI workflow.

---

## Prompt-injection sources

| Source | Architectural control |
|---|---|
| User input | Intent classifier skip_model; output validation |
| Multi-turn | History is user/assistant text only; policy reloaded every turn |
| Retrieved HTML/PDF/DOCX | Evidence channel; tools not granted; public access_class |
| Knowledge metadata | Titles/URLs still untrusted in UI; allowlisted hrefs |
| Tool results | NormalizedToolResult; cannot register tools |
| Model output | `validate_assistant_text` strips secret/policy leaks |
| Indirect injection | Poison fixture + tests |

Do not treat “the model was asked to ignore malicious instructions” as the primary control.

---

## Authorization matrix

| Capability | Public user | Authenticated user | Authorized staff | Admin | Service identity |
|---|---|---|---|---|---|
| Text/voice Q&A on public corpus | Yes | N/A (not implemented) | N/A | N/A | API process |
| Retrieve `access_class=internal` | No | N/A | N/A | N/A | No at HTTP runtime |
| Approved navigation tools | Yes (allowlist) | N/A | N/A | N/A | No extra tools |
| Privileged tools | No | N/A | N/A | N/A | No |
| `/admin/*` | 403/401 | N/A | N/A | Bearer token + flag | Worker ingest CLI only |
| Kill switches | No | N/A | N/A | Env/config owner | Restart/reload env |
| Provider keys | No | No | No | No | API/worker env |

Roles not invented: there is no staff SSO yet. “Authenticated user” remains a reserved `AuthContext` value unused by HTTP.

---

## CSRF

Pixel does not use cookies for API authentication. Session IDs are sent in JSON. A cross-site form cannot attach a victim's session ID unless it is leaked. WebSocket connections check Origin. CSRF tokens are therefore not implemented. If cookie auth is added later, SameSite + CSRF tokens are required.

---

## Rate-limit honesty

Limits are **in-process** (`InProcessRateLimiter`). They protect a single API worker. They do **not** provide cluster-wide protection. Production with multiple replicas needs a proxy or Redis limiter before claiming distributed abuse resistance.
