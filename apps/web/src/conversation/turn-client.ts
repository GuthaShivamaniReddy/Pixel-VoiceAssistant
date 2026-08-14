import { getPublicApiBaseUrl } from "@/lib/env";
import type { LatencyMetrics } from "./latency";
import { EMPTY_METRICS } from "./latency";
import type { RecommendedAction, SourceRef } from "./types";

export type TurnSuccess = {
  sessionId: string;
  turnId: string;
  text: string;
  transcript: string;
  sources: SourceRef[];
  actions: RecommendedAction[];
  audio: ArrayBuffer | null;
  metrics: LatencyMetrics;
  voiceWarning: string | null;
};

export type TurnFailure = {
  code: string;
  message: string;
};

export type TurnClient = {
  submitText: (input: {
    sessionId: string | null;
    turnId: string;
    text: string;
    speak: boolean;
    signal: AbortSignal;
  }) => Promise<TurnSuccess>;
};

function asSources(value: unknown): SourceRef[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is SourceRef => {
    return Boolean(item && typeof item === "object" && "url" in item && "title" in item);
  });
}

function asActions(value: unknown): RecommendedAction[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is RecommendedAction => {
    return Boolean(item && typeof item === "object" && "id" in item && "href" in item);
  });
}

function decodeWav(b64: string | null | undefined): ArrayBuffer | null {
  if (!b64) {
    return null;
  }
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

export class TurnRequestError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export function createHttpTurnClient(): TurnClient {
  return {
    async submitText({ sessionId, turnId, text, speak, signal }) {
      const response = await fetch(`${getPublicApiBaseUrl()}/v1/turns`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ session_id: sessionId, turn_id: turnId, text, speak }),
        signal,
      });
      const body = (await response.json()) as Record<string, unknown>;
      if (!response.ok) {
        const error = (body.error as TurnFailure | undefined) ?? {
          code: "network",
          message: "Request failed",
        };
        throw new TurnRequestError(String(error.code), String(error.message));
      }
      const metrics = (body.metrics as LatencyMetrics | undefined) ?? EMPTY_METRICS;
      return {
        sessionId: String(body.session_id ?? sessionId ?? ""),
        turnId: String(body.turn_id ?? turnId),
        text: String(body.text ?? ""),
        transcript: String(body.transcript ?? text),
        sources: asSources(body.sources),
        actions: asActions(body.actions),
        audio: decodeWav(body.audio_wav_base64 as string | undefined),
        metrics,
        voiceWarning: body.voice_warning ? String(body.voice_warning) : null,
      };
    },
  };
}
