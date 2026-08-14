CREATE TABLE IF NOT EXISTS knowledge_sources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    canonical_url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    access_class TEXT NOT NULL DEFAULT 'public',
    topic TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT '',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'registered',
    content_hash TEXT NOT NULL DEFAULT '',
    version INTEGER NOT NULL DEFAULT 0,
    publication_date TEXT,
    last_fetched_at TIMESTAMPTZ,
    last_updated_at TIMESTAMPTZ,
    error TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES knowledge_sources(id),
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    access_class TEXT NOT NULL,
    topic TEXT NOT NULL,
    audience TEXT NOT NULL,
    source_type TEXT NOT NULL,
    UNIQUE (source_id, version)
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES knowledge_documents(id),
    source_id TEXT NOT NULL REFERENCES knowledge_sources(id),
    ordinal INTEGER NOT NULL,
    heading_path TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    topic TEXT NOT NULL,
    audience TEXT NOT NULL,
    source_type TEXT NOT NULL,
    access_class TEXT NOT NULL,
    version INTEGER NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    embedding vector(1536) NOT NULL,
    indexed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS knowledge_chunks_active_access
    ON knowledge_chunks (active, access_class);
CREATE INDEX IF NOT EXISTS knowledge_chunks_source
    ON knowledge_chunks (source_id);

