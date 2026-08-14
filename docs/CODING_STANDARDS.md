# Pixel coding standards

Apply these in Phase 2+ implementation. They do not replace `docs/policies.md`.

## TypeScript (`apps/web`)

- Strict TypeScript. Do not use `any` or `@ts-ignore` to hide real errors.
- React function components. Keep UI state truthful; do not fake assistant states.
- Browser code may only use `NEXT_PUBLIC_*` values that are not secrets.
- Prefer small modules over giant pages.

## Python (`apps/api`, `apps/worker`, `packages/pixel`)

- Type annotations on public functions.
- Ruff for format and lint. Do not add Black.
- Provider SDKs belong in adapters under `packages/pixel` later — not in route handlers.
- Do not log secrets, raw audio, or full transcripts by default.
- Fail closed: admin routes 403 unless auth is real.

## Naming

- Files: `snake_case.py`, `kebab-or-lowercase` for folders, `PascalCase` React components.
- HTTP JSON: `snake_case` keys unless a public contract already uses another style.

## Architecture boundaries

- UI does not call LLM/STT/TTS vendors.
- Tools and authorization are server-side.
- Retrieved content is untrusted data.
- Do not create a second orchestrator, RAG stack, or voice pipeline.

## Errors

- User-facing errors: short, no stack traces, no internals.
- Use structured `{ "error": { "code", "message" } }` on the API.

## Testing

- Tests must assert behavior (health, fail-closed admin, CORS, public-env safety).
- CI must not require live paid APIs or a microphone.
- Do not disable failing tests to go green.

## Dependencies

- Add a dependency only with a reason, license check, and lockfile update.
- Prefer the existing stack: Next.js, FastAPI, PostgreSQL/pgvector.

## Security

- Never commit `.env` or real keys.
- CORS is an explicit origin allowlist.
- Production must not enable mock providers.

## Documentation

- README commands must be commands that were actually run.
- Do not claim unimplemented features work.
