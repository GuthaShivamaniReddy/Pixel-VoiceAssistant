import sys
from collections.abc import Sequence

from pixel.knowledge.embeddings import HashEmbeddingProvider
from pixel.knowledge.ingest import ingest_fixtures
from pixel.knowledge.store import InMemoryKnowledgeStore


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["ingest"]:
        store = InMemoryKnowledgeStore()
        results = ingest_fixtures(embedder=HashEmbeddingProvider(), store=store)
        indexed = sum(1 for item in results if item.status in {"indexed", "unchanged"})
        print(f"pixel-worker: ingested {indexed} approved fixture sources")
        return 0
    print("pixel-worker: idle (run pixel-worker ingest to index the fixture corpus)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
