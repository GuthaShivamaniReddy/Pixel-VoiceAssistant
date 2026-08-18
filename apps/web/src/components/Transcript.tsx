"use client";

import { useEffect, useRef, useState } from "react";
import type { ConversationTurn as Turn } from "@/conversation/types";
import { ConversationTurn } from "./ConversationTurn";

type TranscriptProps = {
  turns: Turn[];
};

export function Transcript({ turns }: TranscriptProps) {
  const listRef = useRef<HTMLOListElement>(null);
  const endRef = useRef<HTMLLIElement>(null);
  const pinRef = useRef(true);
  const [showJump, setShowJump] = useState(false);

  useEffect(() => {
    if (!pinRef.current) {
      setShowJump(true);
      return;
    }
    endRef.current?.scrollIntoView({ block: "end" });
    setShowJump(false);
  }, [turns]);

  if (turns.length === 0) {
    return null;
  }

  return (
    <div className="transcript-wrap">
      <ol
        ref={listRef}
        className="transcript"
        aria-label="Conversation transcript"
        onScroll={(event) => {
          const node = event.currentTarget;
          const remaining = node.scrollHeight - node.scrollTop - node.clientHeight;
          pinRef.current = remaining < 48;
          setShowJump(!pinRef.current);
        }}
      >
        {turns.map((turn) => (
          <ConversationTurn key={turn.id} turn={turn} />
        ))}
        <li ref={endRef} aria-hidden="true" />
      </ol>
      {showJump ? (
        <button
          type="button"
          className="control control--quiet jump-latest"
          onClick={() => {
            pinRef.current = true;
            endRef.current?.scrollIntoView({ block: "end" });
            setShowJump(false);
          }}
        >
          Jump to latest
        </button>
      ) : null}
    </div>
  );
}
