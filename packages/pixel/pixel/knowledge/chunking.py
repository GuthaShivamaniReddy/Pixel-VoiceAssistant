"""Heading-first semantic chunking with size as a secondary limit."""

from __future__ import annotations

import hashlib

from pixel.knowledge.normalize import content_hash, normalize_text, token_count

MAX_CHARS = 1200


def _stable_id(source_id: str, heading: str, body: str) -> str:
    payload = f"{source_id}|{heading}|{normalize_text(body)}".encode()
    return hashlib.sha256(payload).hexdigest()[:24]


def _split_oversize(text: str) -> list[str]:
    if len(text) <= MAX_CHARS:
        return [text]
    words = text.split()
    parts: list[str] = []
    buf: list[str] = []
    for word in words:
        trial = " ".join([*buf, word])
        if buf and len(trial) > MAX_CHARS:
            parts.append(" ".join(buf))
            buf = [word]
        else:
            buf.append(word)
    if buf:
        parts.append(" ".join(buf))
    return parts


def chunk_blocks(
    blocks: list[tuple[str, str]],
    *,
    source_id: str,
    title: str,
) -> list[dict[str, str | int]]:
    path: list[str] = [title] if title else []
    sections: list[tuple[str, list[str]]] = []
    current_path = " > ".join(path) if path else title
    current: list[str] = []

    def push() -> None:
        nonlocal current
        text = normalize_text("\n".join(current))
        current = []
        if text:
            sections.append((current_path, [text]))

    for kind, raw in blocks:
        text = normalize_text(raw)
        if not text:
            continue
        if kind.startswith("h"):
            push()
            level = int(kind[1]) if kind[1:].isdigit() else 1
            path = path[:level]
            if len(path) < level:
                path.extend([""] * (level - len(path)))
            if path:
                path[-1] = text
            else:
                path = [text]
            current_path = " > ".join(part for part in path if part)
            current = [text]
            continue
        pieces = _split_oversize(text)
        for piece in pieces:
            if sum(len(part) for part in current) + len(piece) > MAX_CHARS:
                push()
                current = [piece]
            else:
                current.append(piece)
    push()

    chunks: list[dict[str, str | int]] = []
    for ordinal, (heading, parts) in enumerate(sections):
        body = normalize_text("\n\n".join(parts))
        if not body:
            continue
        chunks.append(
            {
                "chunk_id": _stable_id(source_id, heading, body),
                "ordinal": ordinal,
                "heading_path": heading,
                "content": body,
                "content_hash": content_hash(body),
                "token_count": token_count(body),
            }
        )
    if not chunks:
        raise ValueError("Chunking produced no content")
    return chunks
