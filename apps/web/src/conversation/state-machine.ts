import type { ConversationEvent, PixelState } from "./types";

const ALLOWED: Record<PixelState, ReadonlySet<ConversationEvent["type"]>> = {
  idle: new Set([
    "START_LISTENING",
    "SUBMIT_TEXT",
    "PERMISSION_DENIED",
    "MIC_UNAVAILABLE",
    "CLEAR",
    "FAIL",
  ]),
  listening: new Set([
    "STOP_LISTEN",
    "CANCEL",
    "FAIL",
    "PERMISSION_DENIED",
    "MIC_UNAVAILABLE",
    "CLEAR",
  ]),
  processing: new Set([
    "RESPONSE_READY",
    "SPEAKING_DONE",
    "FAIL",
    "CANCEL",
    "CLEAR",
    "START_LISTENING",
  ]),
  speaking: new Set([
    "SPEAKING_DONE",
    "STOP_SPEAKING",
    "CANCEL",
    "FAIL",
    "CLEAR",
    "START_LISTENING",
  ]),
  error: new Set(["RETRY", "DISMISS_ERROR", "SUBMIT_TEXT", "CLEAR"]),
  permission_denied: new Set(["SUBMIT_TEXT", "START_LISTENING", "DISMISS_ERROR", "CLEAR"]),
};

export function canHandle(state: PixelState, event: ConversationEvent["type"]): boolean {
  return ALLOWED[state].has(event);
}

export function reduceState(state: PixelState, event: ConversationEvent): PixelState {
  if (!canHandle(state, event.type)) {
    return state;
  }

  switch (event.type) {
    case "START_LISTENING":
      return "listening";
    case "PERMISSION_DENIED":
      return "permission_denied";
    case "MIC_UNAVAILABLE":
      return "error";
    case "STOP_LISTEN":
    case "SUBMIT_TEXT":
      return "processing";
    case "RESPONSE_READY":
      return "speaking";
    case "SPEAKING_DONE":
    case "STOP_SPEAKING":
    case "CANCEL":
    case "RETRY":
    case "DISMISS_ERROR":
    case "CLEAR":
      return "idle";
    case "FAIL":
      return "error";
    default:
      return state;
  }
}

export function isBusy(state: PixelState): boolean {
  return state === "listening" || state === "processing" || state === "speaking";
}
