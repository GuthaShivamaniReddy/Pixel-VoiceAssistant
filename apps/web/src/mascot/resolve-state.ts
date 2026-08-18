import type { ErrorCode, PixelState } from "@/conversation/types";
import type { PixelMascotCue, PixelMascotState } from "./states";

export type PixelMascotInput = {
  assistantState: PixelState;
  muted: boolean;
  errorCode: ErrorCode | null;
  hasConversation: boolean;
  cue: PixelMascotCue;
  retrievalActive: boolean;
  toolActive: boolean;
  speakingHasSources: boolean;
  speakingHasActions: boolean;
};

/**
 * Map live assistant signals to one mascot state.
 * Higher-priority rows win. Never invent RAG/tool/listen/speak.
 */
export function resolvePixelMascotState(input: PixelMascotInput): PixelMascotState {
  const { assistantState } = input;

  if (assistantState === "error" || assistantState === "permission_denied") {
    if (input.errorCode === "network") {
      return "offline";
    }
    return "error";
  }

  if (assistantState === "listening") {
    return "listening";
  }

  if (assistantState === "speaking") {
    if (input.speakingHasActions) {
      return "toolAction";
    }
    if (input.speakingHasSources) {
      return "reading";
    }
    return "speaking";
  }

  if (assistantState === "processing") {
    if (input.toolActive) {
      return "toolAction";
    }
    if (input.retrievalActive) {
      return "searching";
    }
    return "thinking";
  }

  if (input.cue === "clearing") {
    return "clearing";
  }
  if (input.cue === "recovering") {
    return "recovering";
  }
  if (input.cue === "success") {
    return "success";
  }
  if (input.cue === "warning") {
    return "warning";
  }
  if (input.cue === "uncertain") {
    return "uncertain";
  }
  if (input.muted) {
    return "muted";
  }
  if (input.cue === "greeting" && !input.hasConversation) {
    return "greeting";
  }
  return "idle";
}
