import type { SourceRef } from "@/conversation/types";
import { isAllowlistedHref } from "@/conversation/allowlist";

type SourceCardProps = {
  source: SourceRef;
};

export function SourceCard({ source }: SourceCardProps) {
  const safe = isAllowlistedHref(source.url);
  return (
    <article className="source-card">
      <p className="source-card__kicker">
        {source.provenance === "mock"
          ? "Mock source — not live RAG"
          : source.provenance === "retrieval"
            ? "Approved Cyber Florida source"
            : "Public Cyber Florida page"}
      </p>
      <h3>{source.title}</h3>
      <p>{source.description}</p>
      <p>
        {safe ? (
          <a
            href={source.url}
            rel="noreferrer noopener"
            target="_blank"
            aria-label={`${source.name}: ${source.title} (opens in a new tab)`}
          >
            {source.name}
          </a>
        ) : (
          <span>{source.name} (link blocked — not an approved Cyber Florida URL)</span>
        )}
      </p>
    </article>
  );
}
