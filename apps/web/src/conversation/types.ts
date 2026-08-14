export const PIXEL_STATES = [
  "idle",
  "listening",
  "processing",
  "speaking",
  "error",
  "permission_denied",
] as const;

export type PixelState = (typeof PIXEL_STATES)[number];

export type MicPermission = "unknown" | "granted" | "denied" | "unavailable";

export type ErrorCode =
  | "permission_denied"
  | "mic_unavailable"
  | "network"
  | "response_failure"
  | "timeout"
  | "empty"
  | "generic"
  | "stt_failure"
  | "tts_failure"
  | "playback_failure"
  | "capture_failure";

export type Role = "user" | "pixel";

export type SourceRef = {
  title: string;
  name: string;
  url: string;
  description: string;
  provenance: "mock" | "policy" | "none" | "retrieval";
};

export type RecommendedAction = {
  id: string;
  label: string;
  href: string;
};

export type ConversationTurn = {
  id: string;
  role: Role;
  text: string;
  sources: SourceRef[];
  actions: RecommendedAction[];
  metrics?: {
    time_to_transcript_ms: number | null;
    model_latency_ms: number | null;
    tts_latency_ms: number | null;
    time_to_first_audio_ms: number | null;
    total_turn_latency_ms: number | null;
    retrieval_latency_ms?: number | null;
  };
};

export type MockReply =
  | {
      kind: "ok";
      spoken: string;
      sources: SourceRef[];
      actions: RecommendedAction[];
      delayMs: number;
    }
  | {
      kind: "fail";
      code: Exclude<ErrorCode, "permission_denied" | "mic_unavailable">;
      message: string;
      delayMs: number;
    };

export type ConversationEvent =
  | { type: "START_LISTENING" }
  | { type: "PERMISSION_DENIED" }
  | { type: "MIC_UNAVAILABLE" }
  | { type: "STOP_LISTEN" }
  | { type: "SUBMIT_TEXT" }
  | { type: "RESPONSE_READY" }
  | { type: "SPEAKING_DONE" }
  | { type: "FAIL" }
  | { type: "CANCEL" }
  | { type: "STOP_SPEAKING" }
  | { type: "RETRY" }
  | { type: "DISMISS_ERROR" }
  | { type: "CLEAR" };

export const MAX_TURNS = 40;

export const STATE_LABEL: Record<PixelState, string> = {
  idle: "Idle — Pixel is ready",
  listening: "Listening — microphone is on",
  processing: "Processing — Pixel is preparing a reply",
  speaking: "Speaking — Pixel is delivering a reply",
  error: "Error — Pixel needs a recovery action",
  permission_denied: "Microphone permission denied — use text instead",
};
