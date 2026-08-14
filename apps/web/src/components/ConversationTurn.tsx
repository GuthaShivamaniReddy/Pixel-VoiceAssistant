import type { ConversationTurn as Turn } from "@/conversation/types";
import { RecommendedAction } from "./RecommendedAction";
import { SourceCard } from "./SourceCard";

type ConversationTurnProps = {
  turn: Turn;
};

export function ConversationTurn({ turn }: ConversationTurnProps) {
  const label = turn.role === "user" ? "You" : "Pixel";
  return (
    <li className={`turn turn--${turn.role}`}>
      <p className="turn__who">{label}</p>
      <p className="turn__text">{turn.text}</p>
      {turn.sources.length > 0 ? (
        <div className="turn__sources">
          {turn.sources.map((source) => (
            <SourceCard key={`${turn.id}-${source.url}`} source={source} />
          ))}
        </div>
      ) : null}
      {turn.actions.length > 0 ? (
        <div className="turn__actions">
          {turn.actions.map((action) => (
            <RecommendedAction key={action.id} action={action} />
          ))}
        </div>
      ) : null}
      {turn.metrics ? (
        <details className="muted">
          <summary>Turn timing</summary>
          <p data-testid="turn-metrics">
            transcript {turn.metrics.time_to_transcript_ms ?? "—"} ms, model{" "}
            {turn.metrics.model_latency_ms ?? "—"} ms, TTS {turn.metrics.tts_latency_ms ?? "—"} ms,
            first audio {turn.metrics.time_to_first_audio_ms ?? "—"} ms, retrieval{" "}
            {turn.metrics.retrieval_latency_ms ?? "—"} ms, total{" "}
            {turn.metrics.total_turn_latency_ms ?? "—"} ms
          </p>
        </details>
      ) : null}
    </li>
  );
}
