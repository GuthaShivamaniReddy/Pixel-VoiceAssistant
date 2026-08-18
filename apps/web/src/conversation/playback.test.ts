import { describe, expect, it } from "vitest";
import { createQueuePlayback, type PlaybackEngine } from "./playback";

function recordingEngine(): PlaybackEngine & { played: string[] } {
  const played: string[] = [];
  return {
    played,
    activeTurnId: null,
    stop() {
      played.push("stop");
    },
    async playWav(_wav, turnId, hooks) {
      hooks?.onStart?.(turnId);
      played.push(`play:${turnId}`);
    },
  };
}

describe("playback queue", () => {
  it("drops queued audio after stop", async () => {
    const engine = recordingEngine();
    const queue = createQueuePlayback(engine);
    const first = queue.playWav(new ArrayBuffer(4), "a");
    queue.stop();
    await first;
    expect(engine.played).toContain("stop");
  });

  it("does not play a previous turn after a new turn starts", async () => {
    const engine = recordingEngine();
    const queue = createQueuePlayback(engine);
    await queue.playWav(new ArrayBuffer(4), "a");
    await queue.playWav(new ArrayBuffer(4), "b");
    expect(engine.played.filter((item) => item.startsWith("play:"))).toEqual(["play:a", "play:b"]);
  });

  it("forwards start hooks only for the active turn", async () => {
    const started: string[] = [];
    const engine = recordingEngine();
    const queue = createQueuePlayback(engine);
    await queue.playWav(new ArrayBuffer(4), "live", {
      onStart(turnId) {
        started.push(turnId);
      },
    });
    expect(started).toEqual(["live"]);
  });
});
