"""Retrieval over the knowledge store. Retrieved text is untrusted evidence."""

from __future__ import annotations

from time import perf_counter

from pixel.ai import EmbeddingProvider
from pixel.knowledge.embeddings import TOKEN
from pixel.knowledge.models import RetrievalHitSet, RetrievedChunk
from pixel.knowledge.store import KnowledgeStore

DEFAULT_TOP_K = 5
DEFAULT_MIN_SCORE = 0.08
MIN_LEXICAL_OVERLAP = 0.35
_STOP = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "are",
        "of",
        "for",
        "to",
        "in",
        "on",
        "and",
        "or",
        "what",
        "who",
        "how",
        "does",
        "do",
        "you",
        "me",
        "tell",
        "about",
        "please",
        "give",
        "where",
        "when",
        "which",
        "that",
        "this",
        "with",
        "from",
    }
)


def _content_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN.findall(text.lower()):
        if token in _STOP or len(token) <= 2:
            continue
        tokens.add(token)
        if token.endswith("s") and len(token) > 4:
            tokens.add(token[:-1])
    return tokens


def lexical_overlap(query: str, content: str) -> float:
    query_tokens = _content_tokens(query)
    if not query_tokens:
        return 0.0
    content_tokens = _content_tokens(content)
    return len(query_tokens & content_tokens) / len(query_tokens)


def _query_overlap(query: str, content: str) -> float:
    parts = [part.strip() for part in query.split("\n") if part.strip()]
    if not parts:
        return 0.0
    return max(lexical_overlap(part, content) for part in parts)


class KnowledgeRetriever:
    def __init__(
        self,
        store: KnowledgeStore,
        embedder: EmbeddingProvider,
        *,
        top_k: int = DEFAULT_TOP_K,
        min_score: float = DEFAULT_MIN_SCORE,
        access_class: str = "public",
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.top_k = top_k
        self.min_score = min_score
        self.access_class = access_class

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        min_score: float | None = None,
        access_class: str | None = None,
        active_only: bool = True,
    ) -> RetrievalHitSet:
        started = perf_counter()
        cleaned = "\n".join(" ".join(part.split()) for part in query.split("\n")).strip()
        if not cleaned:
            return RetrievalHitSet(
                available=False,
                chunks=(),
                reason="empty_query",
                query=cleaned,
                latency_ms=0,
            )
        queries = [cleaned]
        if "\n" in cleaned:
            current = cleaned.split("\n")[-1].strip()
            prior = cleaned.split("\n")[0].strip()
            if current:
                queries.append(current)
            if prior:
                queries.append(prior)
        merged: dict[str, RetrievedChunk] = {}
        search_ms = 0
        limit = top_k or self.top_k
        floor = min_score if min_score is not None else self.min_score
        access = self.access_class
        del access_class
        for item in queries:
            embedding = tuple(float(value) for value in self.embedder.embed_query(item))
            hits = self.store.search(
                embedding,
                top_k=max(limit * 4, limit),
                min_score=floor,
                access_class=access,
                active_only=active_only,
            )
            search_ms += hits.latency_ms
            for chunk in hits.chunks:
                if _query_overlap(cleaned, chunk.content) < MIN_LEXICAL_OVERLAP:
                    continue
                previous = merged.get(chunk.chunk_id)
                if previous is None or chunk.score > previous.score:
                    merged[chunk.chunk_id] = chunk
        ranked = sorted(merged.values(), key=lambda chunk: chunk.score, reverse=True)
        supported = tuple(ranked[:limit])
        available = bool(supported)
        return RetrievalHitSet(
            available=available,
            chunks=supported,
            reason="ok" if available else "no_acceptable_evidence",
            query=cleaned,
            latency_ms=search_ms + int((perf_counter() - started) * 1000),
        )


_RARE = frozenset(
    {
        "budget",
        "salary",
        "phone",
        "email",
        "cell",
        "director",
        "unpublished",
        "secret",
        "admin",
        "venue",
        "fee",
        "grant",
        "summit",
        "intern",
        "org",
        "chart",
    }
)


def evidence_supports_question(query: str, chunks: tuple) -> bool:
    """Reject hits that share only generic org words when the question asks a specific fact."""
    if not chunks:
        return False
    rare = {token for token in _content_tokens(query) if token.isdigit() or token in _RARE}
    if not rare:
        return True
    blob = " ".join(chunk.content.lower() for chunk in chunks)
    blob_tokens = _content_tokens(blob)
    if rare & blob_tokens:
        return True
    return any(marker in blob for marker in ("not published", "cannot verify", "must not invent"))


def retrieval_query(user_text: str, history: tuple[tuple[str, str], ...] = ()) -> str:
    """Use the current question plus a short prior user turn for follow-ups."""
    current = " ".join(user_text.split()).strip()
    follow = current.lower()
    if history and (
        follow.startswith("what about")
        or follow.startswith("tell me more")
        or follow in {"that one", "the second one", "the first one"}
        or "second one" in follow
        or "beginner" in follow
    ):
        prior_user = next((text for role, text in reversed(history) if role == "user"), "")
        if prior_user:
            return f"{prior_user}\n{current}"
    return current
