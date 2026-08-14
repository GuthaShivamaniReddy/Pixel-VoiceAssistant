# Incident response (minimum)

**Can this be executed today?** No. There is no production Pixel, no provider credentials in-repo, and no kill-switch config.

When operations exist, the on-call engineer must be able to:

1. **Revoke or rotate** a compromised LLM/STT/TTS/embedding credential in the secret manager; restart API/worker.
2. **Disable a tool or provider** via configuration without a full application rewrite (feature flag / allowlist).
3. **Deactivate a poisoned or stale knowledge source** and re-index so chunks are not retrieved.
4. **Roll back** application version, policy version, and knowledge index version independently.
5. **Trace** affected turns with `conversation_id` / `message_id` without expanding log collection.
6. **Communicate** user-visible outage through an approved Cyber Florida/USF channel.

Do not dump transcripts into tickets by default.

Related: `docs/security/`, `docs/product.md` (retention).
