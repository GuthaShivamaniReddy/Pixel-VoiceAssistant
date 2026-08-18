"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  createAudioContext,
  createBrowserCapture,
  type CaptureFactory,
  type CaptureHandle,
} from "./capture";
import { ERROR_COPY } from "./errors";
import { EMPTY_METRICS, type LatencyMetrics } from "./latency";
import { createBrowserMicrophone, type MicrophoneBridge } from "./microphone";
import { isUsableTranscript, normalizeTranscript } from "./normalize";
import { createBrowserPlayback, createQueuePlayback, type PlaybackEngine } from "./playback";
import { createBrowserRealtimeClient, type RealtimeClient } from "./realtime-client";
import { reduceState } from "./state-machine";
import { createHttpSessionClient, type SessionClient } from "./session-client";
import { createHttpTurnClient, TurnRequestError, type TurnClient } from "./turn-client";
import type {
  ConversationEvent,
  ConversationTurn,
  ErrorCode,
  MicPermission,
  PixelState,
} from "./types";
import { MAX_TURNS } from "./types";

export type ConversationController = {
  state: PixelState;
  permission: MicPermission;
  muted: boolean;
  cancelled: boolean;
  errorCode: ErrorCode | null;
  errorTitle: string | null;
  errorDetail: string | null;
  turns: ConversationTurn[];
  draft: string;
  setDraft: (value: string) => void;
  startListening: () => Promise<void>;
  stopListening: (transcript?: string) => void;
  submitText: (text?: string) => void;
  cancel: () => void;
  stopSpeaking: () => void;
  toggleMute: () => void;
  retry: () => void;
  dismissError: () => void;
  clearConversation: () => void;
  confirmClear: () => void;
  closeClearDialog: () => void;
  clearDialogOpen: boolean;
  micStream: MediaStream | null;
};

type Options = {
  microphone?: MicrophoneBridge;
  turnClient?: TurnClient;
  sessionClient?: SessionClient;
  realtime?: RealtimeClient;
  capture?: CaptureFactory;
  playback?: PlaybackEngine;
  onSpeechLevel?: (level: number) => void;
};

const ERROR_CODES: ReadonlySet<string> = new Set([
  "permission_denied",
  "mic_unavailable",
  "network",
  "response_failure",
  "timeout",
  "empty",
  "generic",
  "stt_failure",
  "tts_failure",
  "playback_failure",
  "capture_failure",
]);

function asErrorCode(code: string): ErrorCode {
  return ERROR_CODES.has(code) ? (code as ErrorCode) : "generic";
}

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `turn-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function useConversation(options: Options = {}): ConversationController {
  const [microphone] = useState(() => options.microphone ?? createBrowserMicrophone());
  const [turnClient] = useState(() => options.turnClient ?? createHttpTurnClient());
  const [sessionClient] = useState(() => options.sessionClient ?? createHttpSessionClient());
  const [realtime] = useState(() => options.realtime ?? createBrowserRealtimeClient());
  const [capture] = useState(() => options.capture ?? createBrowserCapture());
  const [playback] = useState(
    () => options.playback ?? createQueuePlayback(createBrowserPlayback()),
  );

  const [state, setState] = useState<PixelState>("idle");
  const [permission, setPermission] = useState<MicPermission>("unknown");
  const [muted, setMuted] = useState(false);
  const [cancelled, setCancelled] = useState(false);
  const [errorCode, setErrorCode] = useState<ErrorCode | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [draft, setDraft] = useState("");
  const [clearDialogOpen, setClearDialogOpen] = useState(false);
  const [micStream, setMicStream] = useState<MediaStream | null>(null);

  const sessionId = useRef<string | null>(null);
  const activeTurnId = useRef<string | null>(null);
  const captureHandle = useRef<CaptureHandle | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const mutedRef = useRef(false);
  const realtimeReady = useRef(false);
  const speechLevelRef = useRef(options.onSpeechLevel);

  useEffect(() => {
    mutedRef.current = muted;
  }, [muted]);

  useEffect(() => {
    speechLevelRef.current = options.onSpeechLevel;
  }, [options.onSpeechLevel]);

  const dispatch = useCallback((event: ConversationEvent) => {
    setState((current) => reduceState(current, event));
  }, []);

  const trimTurns = useCallback((next: ConversationTurn[]) => {
    if (next.length <= MAX_TURNS) {
      return next;
    }
    return next.slice(next.length - MAX_TURNS);
  }, []);

  const stopCapture = useCallback(() => {
    const handle = captureHandle.current;
    captureHandle.current = null;
    setMicStream(null);
    microphone.release();
    return handle?.stop() ?? { pcm: new Int16Array(0), sampleRate: 16000 };
  }, [microphone]);

  const abortActive = useCallback(
    (sendCancel: boolean) => {
      const turnId = activeTurnId.current;
      abortRef.current?.abort();
      abortRef.current = null;
      playback.stop();
      speechLevelRef.current?.(0);
      if (sendCancel && turnId) {
        realtime.cancel(turnId);
      }
      stopCapture();
      activeTurnId.current = null;
    },
    [playback, realtime, stopCapture],
  );

  useEffect(() => {
    return () => {
      abortActive(true);
      realtime.disconnect();
    };
  }, [abortActive, realtime]);

  const fail = useCallback(
    (code: ErrorCode) => {
      setErrorCode(code);
      dispatch({ type: "FAIL" });
    },
    [dispatch],
  );

  const appendTurn = useCallback(
    (turn: ConversationTurn) => {
      setTurns((current) => trimTurns([...current, turn]));
    },
    [trimTurns],
  );

  const finishWithoutSpeech = useCallback(
    (turnId: string, warning: string | null = null) => {
      if (activeTurnId.current !== turnId) {
        return;
      }
      speechLevelRef.current?.(0);
      dispatch({ type: "SPEAKING_DONE" });
      if (warning === "tts_failure") {
        setErrorCode("tts_failure");
      }
      activeTurnId.current = null;
    },
    [dispatch],
  );

  const playTurnAudio = useCallback(
    async (turnId: string, audio: ArrayBuffer) => {
      if (activeTurnId.current !== turnId || mutedRef.current) {
        finishWithoutSpeech(turnId);
        return;
      }
      try {
        await playback.playWav(audio, turnId, {
          onStart(startedTurn) {
            if (activeTurnId.current === startedTurn) {
              dispatch({ type: "RESPONSE_READY" });
            }
          },
          onLevel(level) {
            speechLevelRef.current?.(level);
          },
        });
      } catch {
        speechLevelRef.current?.(0);
        if (activeTurnId.current === turnId) {
          setErrorCode("playback_failure");
        }
      }
      speechLevelRef.current?.(0);
      if (activeTurnId.current === turnId) {
        dispatch({ type: "SPEAKING_DONE" });
        activeTurnId.current = null;
      }
    },
    [dispatch, finishWithoutSpeech, playback],
  );

  const applyAssistant = useCallback(
    async (
      turnId: string,
      text: string,
      sources: ConversationTurn["sources"],
      actions: ConversationTurn["actions"],
      audio: ArrayBuffer | null,
      metrics: LatencyMetrics,
      voiceWarning: string | null,
    ) => {
      if (activeTurnId.current !== turnId) {
        return;
      }
      appendTurn({
        id: `pixel-${turnId}`,
        role: "pixel",
        text,
        sources,
        actions,
        metrics,
      });
      if (voiceWarning === "tts_failure") {
        finishWithoutSpeech(turnId, "tts_failure");
        return;
      }
      if (mutedRef.current || !audio) {
        if (mutedRef.current || voiceWarning) {
          finishWithoutSpeech(turnId);
        }
        return;
      }
      await playTurnAudio(turnId, audio);
    },
    [appendTurn, finishWithoutSpeech, playTurnAudio],
  );

  const runTextTurn = useCallback(
    async (userText: string) => {
      const cleaned = normalizeTranscript(userText);
      if (!isUsableTranscript(cleaned)) {
        return;
      }
      const turnId = newId();
      activeTurnId.current = turnId;
      abortRef.current?.abort();
      const abort = new AbortController();
      abortRef.current = abort;
      appendTurn({ id: `user-${turnId}`, role: "user", text: cleaned, sources: [], actions: [] });
      dispatch({ type: "SUBMIT_TEXT" });
      try {
        const result = await turnClient.submitText({
          sessionId: sessionId.current,
          turnId,
          text: cleaned,
          speak: !mutedRef.current,
          signal: abort.signal,
        });
        if (activeTurnId.current !== turnId) {
          return;
        }
        sessionId.current = result.sessionId || sessionId.current;
        await applyAssistant(
          turnId,
          result.text,
          result.sources,
          result.actions,
          result.audio,
          result.metrics,
          result.voiceWarning,
        );
      } catch (error) {
        if (abort.signal.aborted || activeTurnId.current !== turnId) {
          return;
        }
        if (error instanceof TurnRequestError) {
          if (error.code === "session_expired" || error.code === "unknown_session") {
            sessionId.current = null;
          }
          fail(asErrorCode(error.code));
          return;
        }
        fail("network");
      }
    },
    [appendTurn, applyAssistant, dispatch, fail, turnClient],
  );

  const ensureRealtime = useCallback(async () => {
    if (realtimeReady.current) {
      return;
    }
    await realtime.connect(sessionId.current, {
      onHello(id) {
        sessionId.current = id;
      },
      onTranscript(turnId, text) {
        if (activeTurnId.current !== turnId) {
          return;
        }
        const cleaned = normalizeTranscript(text);
        if (!cleaned) {
          return;
        }
        setTurns((current) => {
          if (current.some((turn) => turn.id === `user-${turnId}`)) {
            return current;
          }
          return trimTurns([
            ...current,
            { id: `user-${turnId}`, role: "user", text: cleaned, sources: [], actions: [] },
          ]);
        });
      },
      onAssistant(turnId, payload) {
        if (activeTurnId.current !== turnId) {
          return;
        }
        void applyAssistant(
          turnId,
          payload.text,
          payload.sources,
          payload.actions,
          null,
          EMPTY_METRICS,
          payload.voiceWarning,
        );
      },
      onAudio(turnId, wav) {
        if (activeTurnId.current !== turnId) {
          return;
        }
        void playTurnAudio(turnId, wav);
      },
      onMetrics(turnId, metrics) {
        if (activeTurnId.current !== turnId) {
          return;
        }
        setTurns((current) =>
          current.map((turn) => (turn.id === `pixel-${turnId}` ? { ...turn, metrics } : turn)),
        );
      },
      onComplete(turnId) {
        if (activeTurnId.current !== turnId) {
          return;
        }
        if (mutedRef.current || playback.activeTurnId !== turnId) {
          finishWithoutSpeech(turnId);
        }
      },
      onCancelled(turnId) {
        if (activeTurnId.current === turnId) {
          activeTurnId.current = null;
        }
      },
      onError(turnId, code) {
        if (turnId && activeTurnId.current !== turnId) {
          return;
        }
        fail(asErrorCode(code));
      },
    });
    realtimeReady.current = true;
  }, [applyAssistant, fail, finishWithoutSpeech, playTurnAudio, playback, realtime, trimTurns]);

  const startListening = useCallback(async () => {
    if (state === "listening") {
      return;
    }
    setCancelled(false);
    setErrorCode(null);
    if (state === "speaking" || state === "processing") {
      abortActive(true);
    }
    const audioContext = createAudioContext();
    const result = await Promise.race([
      microphone.requestAccess(),
      new Promise<Exclude<MicPermission, "unknown">>((resolve) => {
        setTimeout(() => resolve("unavailable"), 5000);
      }),
    ]);
    setPermission(result);
    if (result !== "granted") {
      void audioContext?.close();
      if (result === "denied") {
        setErrorCode("permission_denied");
        dispatch({ type: "PERMISSION_DENIED" });
        return;
      }
      fail("mic_unavailable");
      return;
    }
    const stream = microphone.getStream();
    try {
      captureHandle.current = await capture.start(stream, audioContext ?? undefined);
    } catch {
      setMicStream(null);
      microphone.release();
      fail("capture_failure");
      return;
    }
    setMicStream(stream);
    dispatch({ type: "START_LISTENING" });
  }, [abortActive, capture, dispatch, fail, microphone, state]);

  const stopListening = useCallback(
    (transcript?: string) => {
      if (state !== "listening") {
        return;
      }
      if (transcript !== undefined) {
        stopCapture();
        const cleaned = normalizeTranscript(transcript);
        if (!cleaned) {
          setCancelled(false);
          dispatch({ type: "CANCEL" });
          return;
        }
        dispatch({ type: "STOP_LISTEN" });
        void runTextTurn(cleaned);
        return;
      }
      const recorded = stopCapture();
      const durationMs = recorded.sampleRate
        ? (recorded.pcm.length / recorded.sampleRate) * 1000
        : 0;
      if (durationMs < 180) {
        setCancelled(false);
        dispatch({ type: "CANCEL" });
        return;
      }
      const turnId = newId();
      activeTurnId.current = turnId;
      dispatch({ type: "STOP_LISTEN" });
      void (async () => {
        try {
          await ensureRealtime();
          if (activeTurnId.current !== turnId) {
            return;
          }
          realtime.startTurn(turnId, recorded.sampleRate);
          realtime.sendAudio(recorded.pcm);
          realtime.endTurn(turnId);
        } catch {
          if (activeTurnId.current === turnId) {
            fail("network");
          }
        }
      })();
    },
    [dispatch, ensureRealtime, fail, realtime, runTextTurn, state, stopCapture],
  );

  const submitText = useCallback(
    (text?: string) => {
      const next = (text ?? draft).trim();
      if (!next || state === "processing" || state === "listening" || state === "speaking") {
        return;
      }
      setDraft("");
      setCancelled(false);
      setErrorCode(null);
      void runTextTurn(next);
    },
    [draft, runTextTurn, state],
  );

  const cancel = useCallback(() => {
    abortActive(true);
    setCancelled(true);
    setErrorCode(null);
    dispatch({ type: "CANCEL" });
  }, [abortActive, dispatch]);

  const stopSpeaking = useCallback(() => {
    abortActive(true);
    setCancelled(false);
    dispatch({ type: "STOP_SPEAKING" });
  }, [abortActive, dispatch]);

  const toggleMute = useCallback(() => {
    const next = !muted;
    setMuted(next);
    if (next && state === "speaking") {
      playback.stop();
      dispatch({ type: "STOP_SPEAKING" });
      activeTurnId.current = null;
    }
  }, [dispatch, muted, playback, state]);

  const retry = useCallback(() => {
    setErrorCode(null);
    setCancelled(false);
    dispatch({ type: "RETRY" });
  }, [dispatch]);

  const dismissError = useCallback(() => {
    setErrorCode(null);
    setCancelled(false);
    dispatch({ type: "DISMISS_ERROR" });
  }, [dispatch]);

  const confirmClear = useCallback(() => {
    abortActive(true);
    const existing = sessionId.current;
    setTurns([]);
    setDraft("");
    setErrorCode(null);
    setCancelled(false);
    setClearDialogOpen(false);
    dispatch({ type: "CLEAR" });
    if (existing) {
      void sessionClient.clear(existing).catch(() => {
        sessionId.current = null;
      });
    }
  }, [abortActive, dispatch, sessionClient]);

  const errorTitle = errorCode ? ERROR_COPY[errorCode].title : null;
  const errorDetail = errorCode ? ERROR_COPY[errorCode].detail : null;

  return {
    state,
    permission,
    muted,
    cancelled,
    errorCode,
    errorTitle,
    errorDetail,
    turns,
    draft,
    setDraft,
    startListening,
    stopListening,
    submitText,
    cancel,
    stopSpeaking,
    toggleMute,
    retry,
    dismissError,
    clearConversation: () => setClearDialogOpen(true),
    confirmClear,
    closeClearDialog: () => setClearDialogOpen(false),
    clearDialogOpen,
    micStream,
  };
}
