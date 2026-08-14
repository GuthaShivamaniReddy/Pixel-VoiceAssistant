# Knowledge refresh

**Can this be executed today?** Yes, as a worker/CLI job against the approved registry. There is no public admin UI (still fail-closed).

1. Content owner approves the source URL and it is added to `pixel.knowledge.registry.PUBLIC_SOURCES`.
2. `pixel-worker ingest` (or `ingest_html` / `ingest_approved_url`) fetches or imports HTML.
3. Content is hashed. Unchanged hash skips re-embed.
4. Changed content creates a new document version, chunks, and embeddings.
5. Parser/empty failures keep the last valid index and record `status=failed`.
6. Deactivate a source to drop it from retrieval without destroying history.
7. Run `evals/knowledge` after material corpus changes.

Fail closed: unauthenticated callers never trigger this. `ADMIN_ENABLED` remains false until later phases.

