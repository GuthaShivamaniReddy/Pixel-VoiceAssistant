# Security documentation

**Implemented controls (Phase 8):** CORS allowlist, admin fail-closed with optional bearer token, security headers/CSP, in-process rate limits, request size limits, log redaction, tool/provider/knowledge kill switches, secret-shaped `NEXT_PUBLIC_*` rejection, parameterized SQL, URL/SSRF allowlists, session UUID + TTL.

| Document | Role |
|---|---|
| [overview.md](overview.md) | Phase 0 threat starters |
| [threat-model.md](threat-model.md) | Implementation-tied threat model |
| [security-review.md](security-review.md) | Phase 8 review |
| [data-retention.md](data-retention.md) | Retention by data class |
| [../SECURITY.md](../SECURITY.md) | Control catalog (SEC-* / PRIV-*) |
| [../policies.md](../policies.md) | Behavioral / cyber-safety policy |
| [../decisions/0004-untrusted-rag.md](../decisions/0004-untrusted-rag.md) | RAG trust decision |
| [../decisions/0006-public-sessions-admin-fail-closed.md](../decisions/0006-public-sessions-admin-fail-closed.md) | Authz posture |
| [../runbooks/security-incident.md](../runbooks/security-incident.md) | Incident response |
| [../runbooks/secret-rotation.md](../runbooks/secret-rotation.md) | Rotation procedure |

Hardcoded live credentials: **not found** in the active tree (see `packages/pixel/tests/test_secret_scan.py`). Local Compose uses the documented non-production password `pixel_dev_only`.
