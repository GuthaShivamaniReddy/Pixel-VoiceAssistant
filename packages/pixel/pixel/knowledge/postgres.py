"""PostgreSQL + pgvector knowledge store."""

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

import psycopg

from pixel.knowledge.models import IndexedChunk, RetrievalHitSet, RetrievedChunk, SourceRecord


def _vector_literal(values: tuple[float, ...]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def _source_from_row(row: tuple) -> SourceRecord:
    return SourceRecord(
        id=row[0],
        title=row[1],
        canonical_url=row[2],
        source_type=row[3],
        access_class=row[4],
        topic=row[5],
        audience=row[6],
        active=row[7],
        status=row[8],
        content_hash=row[9],
        version=row[10],
        publication_date=row[11],
        last_fetched_at=row[12],
        last_updated_at=row[13],
        error=row[14],
    )


class PostgresKnowledgeStore:
    def __init__(self, database_url: str) -> None:
        self._url = database_url

    def upsert_source(self, source: SourceRecord) -> None:
        with psycopg.connect(self._url) as conn:
            conn.execute(
                """
                INSERT INTO knowledge_sources (
                    id, title, canonical_url, source_type, access_class, topic, audience,
                    active, status, content_hash, version, publication_date, last_fetched_at,
                    last_updated_at, error
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    canonical_url = EXCLUDED.canonical_url,
                    active = EXCLUDED.active,
                    status = EXCLUDED.status,
                    content_hash = EXCLUDED.content_hash,
                    version = EXCLUDED.version,
                    last_fetched_at = EXCLUDED.last_fetched_at,
                    last_updated_at = EXCLUDED.last_updated_at,
                    error = EXCLUDED.error
                """,
                (
                    source.id,
                    source.title,
                    source.canonical_url,
                    source.source_type,
                    source.access_class,
                    source.topic,
                    source.audience,
                    source.active,
                    source.status,
                    source.content_hash,
                    source.version,
                    source.publication_date,
                    source.last_fetched_at,
                    source.last_updated_at,
                    source.error,
                ),
            )
            conn.commit()

    def get_source(self, source_id: str) -> SourceRecord | None:
        with psycopg.connect(self._url) as conn:
            row = conn.execute(
                """
                SELECT id, title, canonical_url, source_type, access_class, topic, audience,
                       active, status, content_hash, version, publication_date, last_fetched_at,
                       last_updated_at, error
                FROM knowledge_sources WHERE id = %s
                """,
                (source_id,),
            ).fetchone()
        if row is None:
            return None
        return _source_from_row(row)

    def replace_chunks(self, source_id: str, chunks: list[IndexedChunk]) -> None:
        with psycopg.connect(self._url) as conn:
            conn.execute(
                "UPDATE knowledge_chunks SET active = FALSE WHERE source_id = %s",
                (source_id,),
            )
            for chunk in chunks:
                conn.execute(
                    """
                    INSERT INTO knowledge_documents (
                        id, source_id, version, title, canonical_url, content_hash, status,
                        fetched_at, access_class, topic, audience, source_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        chunk.document_id,
                        chunk.source_id,
                        chunk.version,
                        chunk.title,
                        chunk.url,
                        chunk.content_hash,
                        "active",
                        chunk.indexed_at,
                        chunk.access_class,
                        chunk.topic,
                        chunk.audience,
                        chunk.source_type,
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO knowledge_chunks (
                        chunk_id, document_id, source_id, ordinal, heading_path, content,
                        content_hash, token_count, title, url, topic, audience, source_type,
                        access_class, version, active, embedding, indexed_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::vector, %s
                    )
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        active = EXCLUDED.active,
                        embedding = EXCLUDED.embedding,
                        version = EXCLUDED.version
                    """,
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.source_id,
                        chunk.ordinal,
                        chunk.heading_path,
                        chunk.content,
                        chunk.content_hash,
                        chunk.token_count,
                        chunk.title,
                        chunk.url,
                        chunk.topic,
                        chunk.audience,
                        chunk.source_type,
                        chunk.access_class,
                        chunk.version,
                        chunk.active,
                        _vector_literal(chunk.embedding),
                        chunk.indexed_at,
                    ),
                )
            conn.commit()

    def deactivate_source(self, source_id: str) -> None:
        with psycopg.connect(self._url) as conn:
            conn.execute(
                """
                UPDATE knowledge_sources
                SET active = FALSE, status = 'inactive', last_updated_at = %s
                WHERE id = %s
                """,
                (datetime.now(UTC), source_id),
            )
            conn.execute(
                "UPDATE knowledge_chunks SET active = FALSE WHERE source_id = %s",
                (source_id,),
            )
            conn.commit()

    def search(
        self,
        query_embedding: tuple[float, ...],
        *,
        top_k: int,
        min_score: float,
        access_class: str,
        active_only: bool,
    ) -> RetrievalHitSet:
        started = perf_counter()
        literal = _vector_literal(query_embedding)
        if active_only:
            sql = """
                SELECT c.chunk_id, c.content, 1 - (c.embedding <=> %s::vector) AS score,
                       c.source_id, c.document_id, c.title, c.url, c.heading_path,
                       c.access_class, c.version, c.topic, c.audience
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE c.access_class = %s AND c.active = TRUE AND s.active = TRUE
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
            """
        else:
            sql = """
                SELECT c.chunk_id, c.content, 1 - (c.embedding <=> %s::vector) AS score,
                       c.source_id, c.document_id, c.title, c.url, c.heading_path,
                       c.access_class, c.version, c.topic, c.audience
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE c.access_class = %s
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
            """
        with psycopg.connect(self._url) as conn:
            rows = conn.execute(sql, (literal, access_class, literal, top_k)).fetchall()
        hits = []
        for row in rows:
            score = float(row[2])
            if score < min_score:
                continue
            hits.append(
                RetrievedChunk(
                    chunk_id=row[0],
                    content=row[1],
                    score=score,
                    source_id=row[3],
                    document_id=row[4],
                    title=row[5],
                    url=row[6],
                    heading=row[7],
                    access_class=row[8],
                    version=row[9],
                    metadata={"topic": row[10], "audience": row[11]},
                )
            )
        available = bool(hits)
        return RetrievalHitSet(
            available=available,
            chunks=tuple(hits),
            reason="ok" if available else "no_acceptable_evidence",
            query="",
            latency_ms=int((perf_counter() - started) * 1000),
        )
