import type { ConversationTurn as Turn } from "@/conversation/types";
import { ConversationTurn } from "./ConversationTurn";

type TranscriptProps = {
  turns: Turn[];
};

export function Transcript({ turns }: TranscriptProps) {
  if (turns.length === 0) {
    return (
      <div className="transcript transcript--empty">
        <p>No conversation yet. Start listening or type a question.</p>
      </div>
    );
  }

  return (
    <ol className="transcript" aria-label="Conversation transcript">
      {turns.map((turn) => (
        <ConversationTurn key={turn.id} turn={turn} />
      ))}
    </ol>
  );
}
