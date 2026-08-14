# Knowledge refresh (future)

**Can this be executed today?** No ingestion worker or source registry exists.

Intended process (from the specification):

1. Content owner approves the source URL.
2. Authenticated admin registers or updates the source.
3. Job fetches content, hashes, chunks, embeds.
4. Automated sanity checks (minimum content, metadata, parser errors).
5. Knowledge regression suite vs the updated index.
6. Promote the new index generation, or keep the previous active index.
7. Disabled sources must not be retrieved.

Fail closed: unauthenticated callers never trigger this.
