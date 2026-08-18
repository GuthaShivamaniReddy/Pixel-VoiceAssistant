# Secret rotation

Do not invent or paste production credential values in this document.

Pixel loads secrets from process environment (`pydantic-settings`). After rotation, restart API and worker processes so new values are picked up.

| Field | Typical env name |
|---|---|
| AI / STT / TTS / embeddings | `OPENAI_API_KEY` (shared adapter today) |
| Database | `DATABASE_URL` |
| Admin bearer | `ADMIN_TOKEN` |
| Signing secrets | None implemented (no JWT/cookie signing yet) |
| CI/CD | GitHub Actions repository secrets (not in git) |

---

## AI / STT / TTS provider credentials

TRIGGER: Leak, vendor notice, staff departure, routine cadence (UNASSIGNED).

OWNER: Provider owner + deployment owner.

ROTATION STEPS:

1. Create a new key in the vendor console. Do not put it in git or `NEXT_PUBLIC_*`.
2. Store it in the deployment secret manager / host env.
3. Restart Pixel API (and worker if it embeds).
4. Disable or delete the old key after validation.

VALIDATION: Text turn succeeds; `/ready` as expected; logs contain no key material.

ROLLBACK: Restore the previous env value and restart if the new key is invalid. If the old key was leaked, rollback is unsafe — fix the new key instead.

POST-ROTATION CHECK: `pip`/`npm` scans unchanged; `test_public_env` still rejects secret-shaped public keys.

---

## Database credentials

TRIGGER: Leak, Compose password reused in a real environment, staff change.

OWNER: Deployment owner.

ROTATION STEPS:

1. Create a new DB role/password with least privilege (CONNECT + DML on app tables; no CREATEDB if possible).
2. Update `DATABASE_URL`.
3. Restart API/worker.
4. Revoke the old role.

VALIDATION: `/ready` database ok (when configured); knowledge search if Postgres is used.

ROLLBACK: Previous URL only if it was not leaked.

POST-ROTATION CHECK: Confirm the local default `pixel_dev_only` is not used in staging/production.

---

## Admin token

TRIGGER: Leak, suspected admin probing, staff change.

OWNER: Application owner + deployment owner.

ROTATION STEPS:

1. Generate a new token ≥ 32 characters for production.
2. Set `ADMIN_TOKEN` and keep `ADMIN_ENABLED` only if SSO-equivalent controls exist.
3. Restart API.
4. Discard the old token.

VALIDATION: Unauthenticated `/admin/sources` is 401/403. Wrong token 401.

ROLLBACK: Only if the new token cannot be deployed; leaked tokens must not be restored.

POST-ROTATION CHECK: Admin audit log shows `unauthorized` without the token value.

---

## Signing secrets

None in the current architecture (no session JWT, no cookie MAC). If added later, rotate independently of provider keys and invalidate existing sessions.

---

## CI/CD secrets

TRIGGER: GitHub secret leak, compromised workflow.

OWNER: Deployment owner.

ROTATION STEPS:

1. Rotate the GitHub Actions secret in the repository settings.
2. Invalidate the old value.
3. Re-run CI.

VALIDATION: CI green without printing secret values.

ROLLBACK: N/A for leaked cloud tokens.

POST-ROTATION CHECK: Confirm `.env` remains gitignored and examples have empty keys.
