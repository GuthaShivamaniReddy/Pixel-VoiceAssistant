"use client";

import { useEffect, useRef, useState } from "react";
import type { ConversationTurn, ErrorCode, PixelState } from "@/conversation/types";
import { resolvePixelMascotState } from "./resolve-state";
import type { PixelMascotCue, PixelMascotState } from "./states";

const GREETING_MS = 2200;
const CUE_MS = 1200;

function lastPixelTurn(turns: ConversationTurn[]): ConversationTurn | undefined {
  return [...turns].reverse().find((turn) => turn.role === "pixel");
}

function idleCueFromReply(text: string): PixelMascotCue {
  const key = text.toLowerCase();
  if (/cannot verify|will not guess|do not guess/.test(key)) {
    return "uncertain";
  }
  if (/cannot help with attacks|not a scam\. common signs/.test(key)) {
    return "warning";
  }
  return "none";
}

export function useMascotCues(input: {
  assistantState: PixelState;
  turns: ConversationTurn[];
  muted: boolean;
  errorCode: ErrorCode | null;
}): {
  mascotState: PixelMascotState;
  beginClearing: () => void;
  beginRecovering: () => void;
} {
  const [greeting, setGreeting] = useState(true);
  const [cue, setCue] = useState<PixelMascotCue>("none");
  const prevState = useRef(input.assistantState);

  useEffect(() => {
    const timer = window.setTimeout(() => setGreeting(false), GREETING_MS);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    const previous = prevState.current;
    prevState.current = input.assistantState;
    if (previous !== "speaking" || input.assistantState !== "idle") {
      return;
    }
    const last = lastPixelTurn(input.turns);
    let next: PixelMascotCue = "none";
    if (last?.actions.length) {
      next = "success";
    } else if (last?.text) {
      next = idleCueFromReply(last.text);
    }
    if (next === "none") {
      return;
    }
    const start = window.setTimeout(() => setCue(next), 0);
    const end = window.setTimeout(() => setCue("none"), CUE_MS);
    return () => {
      window.clearTimeout(start);
      window.clearTimeout(end);
    };
  }, [input.assistantState, input.turns]);

  useEffect(() => {
    if (cue === "none" || cue === "greeting") {
      return;
    }
    const timer = window.setTimeout(() => setCue("none"), CUE_MS);
    return () => window.clearTimeout(timer);
  }, [cue]);

  const last = lastPixelTurn(input.turns);
  const speaking = input.assistantState === "speaking";
  const mascotState = resolvePixelMascotState({
    assistantState: input.assistantState,
    muted: input.muted,
    errorCode: input.errorCode,
    hasConversation: input.turns.length > 0,
    cue: greeting && input.turns.length === 0 ? "greeting" : cue,
    retrievalActive: false,
    toolActive: false,
    speakingHasSources: Boolean(speaking && last?.sources.length),
    speakingHasActions: Boolean(speaking && last?.actions.length),
  });

  return {
    mascotState,
    beginClearing: () => setCue("clearing"),
    beginRecovering: () => setCue("recovering"),
  };
}
