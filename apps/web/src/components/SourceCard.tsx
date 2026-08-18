import type { SourceRef } from "@/conversation/types";
import { isAllowlistedHref } from "@/conversation/allowlist";

type SourceCardProps = {
  source: SourceRef;
};

function kicker(provenance: SourceRef["provenance"]): string {
  if (provenance === "mock") {
    return "Mock source — not live RAG";
  }
  if (provenance === "retrieval") {
    return "Approved Cyber Florida source";
  }
  return "Official Cyber Florida resource";
}

export function SourceCard({ source }: SourceCardProps) {
  const safe = isAllowlistedHref(source.url);
  return (
    <article className="source-card">
      <p className="source-card__kicker">{kicker(source.provenance)}</p>
      <h3 title={source.title}>{source.title}</h3>
      {source.description ? (
        source.description.length > 140 ? (
          <details>
            <summary>Why this source</summary>
            <p className="source-card__desc">{source.description}</p>
          </details>
        ) : (
          <p className="source-card__desc">{source.description}</p>
        )
      ) : null}
      <p className="source-card__link">
        {safe ? (
          <a
            href={source.url}
            rel="noreferrer noopener"
            target="_blank"
            aria-label={`${source.name}: ${source.title} (opens in a new tab)`}
          >
            Open official page
          </a>
        ) : (
          <span>{source.name} (link blocked — not an approved Cyber Florida URL)</span>
        )}
      </p>
    </article>
  );
}
