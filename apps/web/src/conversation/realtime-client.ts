import { getPublicApiBaseUrl } from "@/lib/env";
import type { LatencyMetrics } from "./latency";
import type { RecommendedAction, SourceRef } from "./types";

export type AssistantPayload = {
  text: string;
  sources: SourceRef[];
  actions: RecommendedAction[];
  voiceWarning: string | null;
};

export type RealtimeHandlers = {
  onHello: (sessionId: string) => void;
  onTranscript: (turnId: string, text: string) => void;
  onAssistant: (turnId: string, payload: AssistantPayload) => void;
  onAudio: (turnId: string, wav: ArrayBuffer) => void;
  onMetrics: (turnId: string, metrics: LatencyMetrics) => void;
  onComplete: (turnId: string) => void;
  onCancelled: (turnId: string) => void;
  onError: (turnId: string | null, code: string, message: string) => void;
};

export type RealtimeClient = {
  connect: (sessionId: string | null, handlers: RealtimeHandlers) => Promise<void>;
  disconnect: () => void;
  startTurn: (turnId: string, sampleRate: number) => void;
  sendAudio: (pcm: Int16Array) => void;
  endTurn: (turnId: string) => void;
  cancel: (turnId: string) => void;
};

function wsUrl(): string {
  const http = getPublicApiBaseUrl();
  return `${http.replace(/^http/i, "ws").replace(/\/$/, "")}/v1/realtime`;
}

export function createBrowserRealtimeClient(): RealtimeClient {
  let socket: WebSocket | null = null;
  let audioTurnId: string | null = null;

  function sendJson(payload: Record<string, unknown>) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  }

  function handleJson(handlers: RealtimeHandlers, raw: string) {
    const payload = JSON.parse(raw) as Record<string, unknown>;
    const type = String(payload.type ?? "");
    const turnId = payload.turn_id ? String(payload.turn_id) : null;
    if (type === "hello_ok" && payload.session_id) {
      handlers.onHello(String(payload.session_id));
    }
    if (type === "audio_start" && turnId) {
      audioTurnId = turnId;
    }
    if (type === "final_transcript" && turnId) {
      handlers.onTranscript(turnId, String(payload.text ?? ""));
    }
    if (type === "assistant_text" && turnId) {
      handlers.onAssistant(turnId, {
        text: String(payload.text ?? ""),
        sources: (payload.sources as SourceRef[]) ?? [],
        actions: (payload.actions as RecommendedAction[]) ?? [],
        voiceWarning: payload.voice_warning ? String(payload.voice_warning) : null,
      });
    }
    if (type === "metrics" && turnId) {
      handlers.onMetrics(turnId, {
        time_to_transcript_ms: (payload.time_to_transcript_ms as number | null) ?? null,
        model_latency_ms: (payload.model_latency_ms as number | null) ?? null,
        tts_latency_ms: (payload.tts_latency_ms as number | null) ?? null,
        time_to_first_audio_ms: (payload.time_to_first_audio_ms as number | null) ?? null,
        total_turn_latency_ms: (payload.total_turn_latency_ms as number | null) ?? null,
        retrieval_latency_ms: (payload.retrieval_latency_ms as number | null) ?? null,
      });
    }
    if (type === "turn_complete" && turnId) {
      handlers.onComplete(turnId);
    }
    if (type === "cancelled" && turnId) {
      handlers.onCancelled(turnId);
    }
    if (type === "error") {
      handlers.onError(
        turnId,
        String(payload.code ?? "generic"),
        String(payload.message ?? "Error"),
      );
    }
  }

  return {
    async connect(sessionId, handlers) {
      this.disconnect();
      const next = new WebSocket(wsUrl());
      next.binaryType = "arraybuffer";
      socket = next;
      await new Promise<void>((resolve, reject) => {
        next.onopen = () => {
          sendJson({ type: "hello", session_id: sessionId });
          resolve();
        };
        next.onerror = () => reject(new Error("realtime_failed"));
      });
      next.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
          if (audioTurnId) {
            handlers.onAudio(audioTurnId, event.data);
          }
          return;
        }
        if (typeof event.data === "string") {
          handleJson(handlers, event.data);
        }
      };
    },
    disconnect() {
      audioTurnId = null;
      socket?.close();
      socket = null;
    },
    startTurn(turnId, sampleRate) {
      sendJson({ type: "start_turn", turn_id: turnId, sample_rate: sampleRate });
    },
    sendAudio(pcm) {
      if (socket && socket.readyState === WebSocket.OPEN) {
        const copy = pcm.buffer.slice(pcm.byteOffset, pcm.byteOffset + pcm.byteLength);
        socket.send(copy);
      }
    },
    endTurn(turnId) {
      sendJson({ type: "end_turn", turn_id: turnId });
    },
    cancel(turnId) {
      sendJson({ type: "cancel", turn_id: turnId });
    },
  };
}
