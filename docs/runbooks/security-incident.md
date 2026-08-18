# Security incident runbook

**Can this be executed today?** Partially. Kill switches and source deactivation exist as configuration and code. Production on-call names and institutional reporting channels are **UNASSIGNED**.

Do not dump transcripts into tickets by default.

## Roles (Phase 0; people UNASSIGNED)

| Role | Responsibility |
|---|---|
| Security incident owner | Triage, containment, post-incident review |
| Application owner | Pixel service behavior and releases |
| Knowledge owner | Source approval and bad-source decisions |
| Provider owner | LLM/STT/TTS/embedding vendor accounts |
| Deployment owner | Env, secrets, restarts, CI/CD |

---

## DETECTION

- HTTP 401/403 spikes on `/admin/*`
- 429 rate-limit spikes
- `security_event type=prompt_injection` volume
- `tool_audit status=unauthorized|invalid_destination`
- Provider errors / kill-switch fallbacks
- User reports of unsafe answers or bad links

## TRIAGE

1. Note `x-correlation-id`, time window, env (`PIXEL_ENV`).
2. Classify: secret leak, abuse, poisoned source, unsafe tool, provider compromise, availability.
3. Do not paste secrets, OTPs, or raw audio into chat.

## CONTAINMENT

Follow the matching procedure below. Prefer configuration kill switches over rewriting prompts.

## SECRET ROTATION

See `secret-rotation.md`. Rotate any credential that may have been exposed. Do not reuse it.

## PROVIDER DISABLEMENT

```text
PROVIDER FAILING / COMPROMISED
↓
Set LLM_ENABLED / STT_ENABLED / TTS_ENABLED = false (as needed)
↓
Restart the API process so Settings reload
↓
ENABLE FALLBACK: text-only if STT/TTS off; canned fallback if LLM off
↓
VERIFY /health and a text turn
↓
ROTATE CREDENTIALS IF REQUIRED
```

Current Settings load at process start. There is no hot admin UI. A restart is required after env change.

## TOOL DISABLEMENT

```text
TOOL BEHAVING UNSAFELY
↓
TOOLS_ENABLED=false  OR  DISABLED_TOOLS=navigate_to_url,...  OR  SIDE_EFFECTING_TOOLS_ENABLED=false
↓
Restart API
↓
PRESERVE AUDIT DATA (logs)
↓
VERIFY the tool returns unavailable / is not executed
↓
INVESTIGATE
↓
FIX
↓
Run tool + safety regression tests
```

## BAD SOURCE REMOVAL

```text
SOURCE IDENTIFIED AS BAD
↓
DEACTIVATE SOURCE (`KnowledgeStore.deactivate_source`)
↓
REMOVE FROM RETRIEVAL (inactive chunks/sources are excluded)
↓
INVALIDATE / REBUILD INDEX if the store requires it
↓
VERIFY the source_id is absent from retrieve()
↓
INVESTIGATE AFFECTED ANSWERS (correlation IDs; do not export full transcripts by default)
```

HTTP admin ingest is not enabled. Local/fixture deactivation is via store API/tests/worker operations.

## LOG / TELEMETRY REVIEW

Search for `security_event`, `admin_audit`, `tool_audit`, `rate_limited`. Confirm redaction (`[REDACTED]`). Do not broaden collection during the incident.

## RECOVERY

Re-enable providers/tools only after validation. Redeploy if a code defect was fixed. Confirm CORS, admin still fail-closed, and a Cyber Florida grounded question still cites an approved source.

## POST-INCIDENT REVIEW

Add a regression test where practical. Update this runbook if a step was missing. Organizational notification paths remain UNASSIGNED.
