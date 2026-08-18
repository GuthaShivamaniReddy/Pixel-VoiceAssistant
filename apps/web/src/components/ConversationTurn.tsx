import type { ConversationTurn as Turn } from "@/conversation/types";
import { PixelMiniAvatar } from "./PixelMiniAvatar";
import { RecommendedAction } from "./RecommendedAction";
import { SourceCard } from "./SourceCard";

type ConversationTurnProps = {
  turn: Turn;
};

function replyTone(text: string): "uncertain" | "warning" | null {
  if (/cannot verify|will not guess|do not guess/.test(text)) {
    return "uncertain";
  }
  if (
    /scam|suspicious|compromis|don't click|do not click|stop using that link|do not enter passwords/i.test(
      text,
    )
  ) {
    return "warning";
  }
  return null;
}

function toneClass(turn: Turn): string {
  if (turn.role !== "pixel") {
    return "";
  }
  const tone = replyTone(turn.text);
  return tone ? ` turn--${tone}` : "";
}

function toneKicker(turn: Turn): string | null {
  if (turn.role !== "pixel") {
    return null;
  }
  const tone = replyTone(turn.text);
  if (tone === "uncertain") {
    return "Could not verify from an approved source";
  }
  if (tone === "warning") {
    return "Security guidance — warning signs, not a verdict";
  }
  return null;
}

export function ConversationTurn({ turn }: ConversationTurnProps) {
  const label = turn.role === "user" ? "You" : "Pixel";
  const kicker = toneKicker(turn);
  return (
    <li className={`turn turn--${turn.role}${toneClass(turn)}`}>
      {kicker ? <p className="turn__kicker">{kicker}</p> : null}
      <p className="turn__who">
        {turn.role === "pixel" ? (
          <PixelMiniAvatar
            state={kicker?.startsWith("Security") ? "warning" : kicker ? "reading" : "idle"}
          />
        ) : null}
        {label}
      </p>
      <p className="turn__text">{turn.text}</p>
      {turn.sources.length > 0 ? (
        <div className="turn__sources">
          <p className="turn__section-label">Sources</p>
          {turn.sources.map((source) => (
            <SourceCard key={`${turn.id}-${source.url}`} source={source} />
          ))}
        </div>
      ) : null}
      {turn.actions.length > 0 ? (
        <div className="turn__actions">
          <p className="turn__section-label">Next step</p>
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
