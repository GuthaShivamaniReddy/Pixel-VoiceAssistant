"""Apply knowledge schema migrations against PostgreSQL + pgvector."""

from __future__ import annotations

from pathlib import Path

import psycopg


def _statements(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [part.strip() for part in text.split(";") if part.strip()]


def upgrade(database_url: str) -> None:
    up = Path(__file__).parent / "sql" / "001_knowledge.up.sql"
    with psycopg.connect(database_url) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        for statement in _statements(up):
            conn.execute(statement)  # type: ignore[call-overload]
        conn.commit()


def downgrade(database_url: str) -> None:
    down = Path(__file__).parent / "sql" / "001_knowledge.down.sql"
    with psycopg.connect(database_url) as conn:
        for statement in _statements(down):
            conn.execute(statement)  # type: ignore[call-overload]
        conn.commit()
