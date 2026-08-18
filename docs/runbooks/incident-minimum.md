# Incident response (minimum)

**Can this be executed today?** Partially. Use the full runbooks:

- [security-incident.md](security-incident.md)
- [secret-rotation.md](secret-rotation.md)

Named on-call people remain UNASSIGNED. Institutional reporting channels remain UNASSIGNED.

When operations exist, the on-call engineer must be able to:

1. **Revoke or rotate** a compromised LLM/STT/TTS/embedding credential; restart API/worker.
2. **Disable a tool or provider** via `TOOLS_ENABLED`, `DISABLED_TOOLS`, `LLM_ENABLED`, `STT_ENABLED`, `TTS_ENABLED` (restart required).
3. **Deactivate a poisoned or stale knowledge source** so chunks are not retrieved.
4. **Roll back** application version, policy version, and knowledge index version independently.
5. **Trace** affected turns with `correlation_id` / `session_id` without expanding log collection.
6. **Communicate** user-visible outage through an approved Cyber Florida/USF channel.

Do not dump transcripts into tickets by default.
