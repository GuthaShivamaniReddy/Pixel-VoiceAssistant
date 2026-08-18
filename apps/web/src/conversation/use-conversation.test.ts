import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { createStubMicrophone } from "./microphone";
import { MockConversationProvider } from "./mock-provider";
import { TurnRequestError, type TurnClient } from "./turn-client";
import { EMPTY_METRICS } from "./latency";
import { useConversation } from "./use-conversation";
import type { CaptureFactory } from "./capture";
import type { PlaybackEngine } from "./playback";

function fakePlayback(): PlaybackEngine {
  return {
    activeTurnId: null,
    stop() {
      /* no audio in unit tests */
    },
    async playWav(_wav, turnId, hooks) {
      hooks?.onStart?.(turnId);
    },
  };
}

function fakeCapture(): CaptureFactory {
  return {
    async start() {
      return {
        sampleRate: 16000,
        stop() {
          return { pcm: new Int16Array(3200), sampleRate: 16000 };
        },
      };
    },
  };
}

function fakeTurns(): TurnClient {
  const provider = new MockConversationProvider();
  return {
    async submitText({ text, speak, signal }) {
      if (signal.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }
      const reply = provider.respond(text);
      if (reply.kind === "fail") {
        throw new TurnRequestError(reply.code, reply.message);
      }
      return {
        sessionId: "s1",
        turnId: "t1",
        text: reply.spoken,
        transcript: text,
        sources: reply.sources,
        actions: reply.actions,
        audio: speak ? new Uint8Array([1, 2, 3, 4]).buffer : null,
        metrics: EMPTY_METRICS,
        voiceWarning: null,
      };
    },
  };
}

function setup(micResult: "granted" | "denied" | "unavailable" = "granted") {
  const hook = renderHook(() =>
    useConversation({
      microphone: createStubMicrophone(micResult),
      turnClient: fakeTurns(),
      sessionClient: {
        async create() {
          return { sessionId: "s1" };
        },
        async clear() {
          /* unit tests do not hit the API */
        },
      },
      playback: fakePlayback(),
      capture: fakeCapture(),
    }),
  );
  return hook;
}

describe("useConversation", () => {
  it("walks idle → listening → processing → speaking → idle", async () => {
    const { result } = setup();

    expect(result.current.state).toBe("idle");
    await act(async () => {
      await result.current.startListening();
    });
    expect(result.current.state).toBe("listening");

    await act(async () => {
      result.current.stopListening("What is Cyber Florida?");
    });
    await waitFor(() => {
      expect(result.current.turns.some((turn) => turn.role === "pixel")).toBe(true);
    });
    expect(result.current.state).toBe("idle");
  });

  it("submits text and rejects empty input", async () => {
    const { result } = setup();

    act(() => {
      result.current.submitText();
    });
    expect(result.current.state).toBe("idle");
    expect(result.current.turns).toHaveLength(0);

    act(() => {
      result.current.setDraft("Explain phishing.");
    });
    await act(async () => {
      result.current.submitText();
    });
    await waitFor(() => {
      expect(result.current.turns[0]?.text).toMatch(/phishing/i);
    });
    expect(result.current.draft).toBe("");
    expect(result.current.state).toBe("idle");
  });

  it("submits an explicit starter prompt without using the draft", async () => {
    const { result } = setup();
    act(() => {
      result.current.setDraft("should not send");
    });
    await act(async () => {
      result.current.submitText("What is Cyber Florida?");
    });
    await waitFor(() => {
      expect(
        result.current.turns.some((turn) => /florida center for cybersecurity/i.test(turn.text)),
      ).toBe(true);
    });
    expect(result.current.draft).toBe("");
  });

  it("handles microphone denied and unavailable", async () => {
    const denied = setup("denied");
    await act(async () => {
      await denied.result.current.startListening();
    });
    expect(denied.result.current.state).toBe("permission_denied");
    expect(denied.result.current.permission).toBe("denied");

    const missing = setup("unavailable");
    await act(async () => {
      await missing.result.current.startListening();
    });
    expect(missing.result.current.state).toBe("error");
    expect(missing.result.current.errorCode).toBe("mic_unavailable");
  });

  it("cancels processing and can recover from a mock failure", async () => {
    const { result } = setup();

    await act(async () => {
      result.current.setDraft("simulate network error");
      result.current.submitText();
      result.current.cancel();
    });
    expect(result.current.state).toBe("idle");
    expect(result.current.cancelled).toBe(true);

    act(() => {
      result.current.setDraft("simulate network error");
    });
    await act(async () => {
      result.current.submitText();
    });
    await waitFor(() => {
      expect(result.current.state).toBe("error");
    });
    act(() => {
      result.current.retry();
    });
    expect(result.current.state).toBe("idle");
  });

  it("clears conversation, stops speaking, and toggles mute", async () => {
    const { result } = setup();

    act(() => {
      result.current.setDraft("Explain phishing.");
    });
    await act(async () => {
      result.current.submitText();
    });
    await waitFor(() => {
      expect(result.current.turns.length).toBeGreaterThan(0);
    });

    act(() => {
      result.current.toggleMute();
    });
    expect(result.current.muted).toBe(true);

    act(() => {
      result.current.confirmClear();
    });
    expect(result.current.turns).toHaveLength(0);
    expect(result.current.state).toBe("idle");
  });

  it("ignores stale turn results after cancel", async () => {
    let release: ((value: void) => void) | undefined;
    const delayed: TurnClient = {
      async submitText({ text, signal }) {
        await new Promise<void>((resolve, reject) => {
          release = resolve;
          signal.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
        });
        return {
          sessionId: "s1",
          turnId: "late",
          text: `late:${text}`,
          transcript: text,
          sources: [],
          actions: [],
          audio: null,
          metrics: EMPTY_METRICS,
          voiceWarning: null,
        };
      },
    };
    const hook = renderHook(() =>
      useConversation({
        microphone: createStubMicrophone("granted"),
        turnClient: delayed,
        sessionClient: {
          async create() {
            return { sessionId: "s1" };
          },
          async clear() {
            /* unused */
          },
        },
        playback: fakePlayback(),
        capture: fakeCapture(),
      }),
    );
    act(() => {
      hook.result.current.setDraft("What is Cyber Florida?");
    });
    await act(async () => {
      hook.result.current.submitText();
    });
    expect(hook.result.current.state).toBe("processing");
    act(() => {
      hook.result.current.cancel();
    });
    await act(async () => {
      release?.();
      await Promise.resolve();
    });
    expect(hook.result.current.turns.some((turn) => turn.text.startsWith("late:"))).toBe(false);
    expect(hook.result.current.state).toBe("idle");
  });

  it("keeps the transcript when muted and skips speaking", async () => {
    const { result } = setup();
    act(() => {
      result.current.toggleMute();
    });
    act(() => {
      result.current.setDraft("Explain phishing.");
    });
    await act(async () => {
      result.current.submitText();
    });
    await waitFor(() => {
      expect(result.current.turns.some((turn) => turn.role === "pixel")).toBe(true);
    });
    expect(result.current.state).toBe("idle");
    expect(result.current.muted).toBe(true);
  });
});
