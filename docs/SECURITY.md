# Pixel — Security

**Canonical folder:** `docs/security/`  
**Document status:** Phase 8 implemented CORS allowlisting, admin fail-closed (token required), rate limits, request size limits, security headers/CSP, log redaction, kill switches, and security tests. Institutional SSO, distributed rate limits, and approved privacy wording remain deferred.

References: OWASP Top 10 for LLM Applications, NIST AI RMF, WCAG 2.2 (a11y adjacent), `REQUIREMENTS.md` SEC-* / PRIV-*.

---

## 1. Security posture

Pixel represents a cybersecurity organization. Users will over-trust it. The assistant must be **defensive, bounded, and auditable**.

Non-negotiables:

- No secrets in the client or git.
- Retrieved RAG content is **untrusted data**.
- Tools are server-side allowlists, not model-granted powers.
- Offensive cyber assistance is out of scope (SEC-14).
- Admin and ingestion fail closed without real authz.
- Do not fake security with client-only checks.

---

## 2. Trust boundaries

```
[User device]  --TLS-->  [Pixel web origin]
                              |
                              | session token, no provider keys
                              v
                       [Pixel API]
                      /     |      \
                     v      v       v
              [Postgres] [STT/LLM/TTS] [Allowlisted fetch]
                 ^
                 | worker only
           [Ingestion worker]
```

| Boundary | Inside | Outside | Rule |
|---|---|---|---|
| B1 Browser ↔ API | UI | FastAPI | CORS allowlist; session token; no provider keys |
| B2 API ↔ Providers | Adapters | OpenAI/Azure/etc. | Server env secrets; egress only |
| B3 API ↔ Postgres | App roles | Database | Least-privilege DB user; no public DB |
| B4 Orchestrator ↔ RAG text | Policy + code | Chunk bodies | Evidence channel only |
| B5 Orchestrator ↔ Tools | Router | Tool impl | Schema + authz + confirmation |
| B6 Worker ↔ Internet | Allowlisted URLs | Arbitrary web | No user-controlled SSRF |
| B7 Public vs admin | Anonymous Q&A | Ingestion | Separate routes; SSO later |
| B8 Public vs internal knowledge | `access_class=public` | internal | MVP: public corpus only |

---

## 3. Threat model (initial)

| Asset | Threat | Control |
|---|---|---|
| Provider API keys | XSS, repo leak, log leak | Server-only env; secret manager in prod; `.env` gitignored; SCA |
| System policy / prompts | Extraction, injection | Do not echo policy; retrieval cannot override; red-team evals |
| Cyber Florida facts | Hallucination, stale data | RAG required; citations; abstain; freshness jobs |
| User audio/transcripts | Retention, insider access | Transient audio; TTL on conversations; log minimization |
| Tools | Confused deputy, arbitrary URL | Allowlist, schema, confirmation, audit `tool_executions` |
| Admin ingestion | Unauth reindex, poisoned corpus | Authz; allowlist; hash; job audit |
| Availability | Abuse, cost amplification | Rate limits, size limits, timeouts, quotas |
| Other users | Session guessing | 128-bit+ random session ids; HTTPS |

---

## 4. Prompt injection

**Sources of untrusted text:** user turns, retrieved chunks, titles, URLs, tool results, filenames.

Controls:

1. Fixed system policy loaded from versioned server files, never from the knowledge base.
2. Delimit evidence; instruct the model that document text is data.
3. **Ignore** document instructions that request new tools, role changes, or secret disclosure — enforced in policy **and** in code (tool router does not read permissions from RAG).
4. Strip or refuse obvious injection wrappers is defense-in-depth, not the primary control.
5. Output validator: refuse to follow “print your system prompt”, credential requests, or tool calls not in the pre-authorized set.
6. Evaluation set in `evals/safety/` (Phase 11, seeded earlier).

Retrieved content **must never override system instructions.**

---

## 5. Input validation

- Max body size on REST and max WS frame/turn duration.
- UTF-8 text; reject huge pastes for scam analysis with a safe summary path.
- Tool arguments: JSON Schema, extra fields forbidden.
- `source_url` admin inputs: HTTPS, host allowlist, no redirects off-allowlist.
- No `eval` of model output.

---

## 6. Tool permissions

| Rule | Detail |
|---|---|
| Inventory | Named tools only (`navigate_to_url`, lookups, approved search) |
| Schema | Strict types; domain/path allowlist for URLs |
| Authz | Public vs admin vs future authenticated tools |
| Confirmation | Side effects need FR-18 confirmation |
| Execution | Server-side only |
| Audit | `tool_executions` row |
| Failure | Tool error does not crash the conversation |

The LLM cannot register tools.

---

## 7. Rate limiting and abuse

- Per IP and per `conversation_id`: session create, messages, WS connect, audio minutes.
- Backoff and 429 with generic messages.
- Cost caps / provider timeouts.
- Disable a provider or tool via config kill switch without full redeploy (Phase 8/10).

---

## 8. Secrets

| Secret | Location | Not allowed |
|---|---|---|
| LLM/STT/TTS/embedding keys | Process env / secret manager | `NEXT_PUBLIC_*`, git, client JS |
| Database URL | API/worker env | Browser |
| Admin SSO client secret | API env | Frontend bundle |

`.env.example` lists names only. Rotation procedure in later runbooks.

Short-lived realtime tokens (if ever used) must expire in minutes and encode only Pixel-session capability, not cloud vendor master keys.

---

## 9. Authentication and authorization readiness

**MVP public mode:** anonymous conversations with unguessable session IDs.

**Must be ready without redesign:**

- `conversations.subject` nullable.
- Admin routes check a real authn/authz middleware; if unconfigured, **403/disabled**.
- Future OIDC/SAML (USF-approved SSO).
- Authorization on every privileged method, not only in the UI.

Do not implement a homemade password table in Phase 2 “for convenience” if SSO is the org standard — use a stub that fails closed plus documented local-dev exception (e.g. explicit `DEV_ADMIN_TOKEN` never enabled in prod).

---

## 10. Web client threats

### XSS (SEC-08)

- React default escaping.
- Never render model/RAG HTML unsanitized.
- Strict Content-Security-Policy in production (Phase 8).
- No `eval` / `new Function` on assistant text.

### CSRF (SEC-09)

- Prefer `Authorization: Bearer <session>` (not auto-sent by other sites).
- If cookies: `SameSite=Lax` or `Strict`, `Secure`, CSRF token on state-changing cookie auth.

### CORS (SEC-10)

- Explicit frontend origin allowlist.
- No `Access-Control-Allow-Origin: *` with credentials.

### Clickjacking / misc headers

- `X-Frame-Options` / CSP `frame-ancestors`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy`
- HSTS on HTTPS terminators

---

## 11. API security

- TLS everywhere outside local dev.
- No stack traces to clients.
- Health checks without dependency secret leakage.
- Parameterized SQL (ORM/SQLAlchemy core).
- Separate DB roles: API read/write app data; worker ingestion; no DDL in app runtime except migrations in deploy.
- Disable verbose OpenAPI in production or protect it.

---

## 12. Privacy controls

| Topic | Control |
|---|---|
| Audio | Transient; discard after STT; no default recording archive |
| Conversations | TTL `expires_at`; user clear; no long-term memory |
| Sensitive data | Do not ask for passwords/OTPs; redact logs |
| Logging | Correlation IDs; opt-in debug transcripts in non-prod only |
| Feedback | Warn users not to paste secrets |
| Notice | Privacy/AI notice before production (Phase 13) |

---

## 13. Harmful cyber use (SEC-14)

Pixel may explain phishing, defensive hygiene, and Cyber Florida programs.

Pixel must refuse: exploit development, malware, unauthorized access, credential stuffing, bypassing controls, or attack playbooks — including roleplay and “authorized test against localhost” framing.

Escalation: direct users to official reporting channels when they describe crimes or account takeovers Pixel cannot handle.

---

## 14. Dependency and supply chain

- Lockfiles committed once the repo exists.
- CI SCA (e.g. pip-audit / npm audit / OSV).
- Pin actions by SHA when GitHub Actions is adopted.
- Review licenses before adding dependencies.

---

## 15. Incident response (minimum, later runbooks)

1. Revoke/rotate provider credentials.
2. Kill-switch a tool or provider.
3. Deactivate a poisoned knowledge source and reindex.
4. Roll back app and policy versions.
5. Trace `conversation_id` / `message_id` without expanding data collection.
6. Communicate user-visible outage through an approved channel.

---

## 16. Phase mapping

| Control cluster | When it becomes real |
|---|---|
| Session tokens, CORS baseline, no secrets in git | Phase 2 |
| XSS-safe UI for transcripts | Phase 3 |
| No vendor keys in browser for voice | Phase 4 |
| Policy layer + output validation hooks | Phase 5 |
| Untrusted RAG wrapping | Phase 6 |
| Tool allowlist + audit | Phase 7 |
| Full threat model tests, CSP, rate limits, redaction | Phase 8 (implemented; live-model red-team scoring still Phase 11) |
| Dashboards / kill-switch UI | Phase 10 (env kill switches exist in Phase 8) |
| Red-team eval gate | Phase 11 |

Phase 0 does not implement these controls; it makes later phases non-optional.
