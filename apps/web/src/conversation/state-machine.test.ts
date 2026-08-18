import { describe, expect, it } from "vitest";
import { canHandle, isBusy, reduceState } from "./state-machine";

describe("conversation state machine", () => {
  it("allows idle to listening", () => {
    expect(reduceState("idle", { type: "START_LISTENING" })).toBe("listening");
  });

  it("allows listening to processing", () => {
    expect(reduceState("listening", { type: "STOP_LISTEN" })).toBe("processing");
  });

  it("allows processing to idle when speech is skipped", () => {
    expect(reduceState("processing", { type: "SPEAKING_DONE" })).toBe("idle");
  });

  it("allows processing to speaking", () => {
    expect(reduceState("processing", { type: "RESPONSE_READY" })).toBe("speaking");
  });

  it("allows speaking to idle", () => {
    expect(reduceState("speaking", { type: "SPEAKING_DONE" })).toBe("idle");
  });

  it("allows error to idle", () => {
    expect(reduceState("error", { type: "RETRY" })).toBe("idle");
    expect(reduceState("error", { type: "DISMISS_ERROR" })).toBe("idle");
  });

  it("rejects impossible listening to speaking", () => {
    expect(canHandle("listening", "RESPONSE_READY")).toBe(false);
    expect(reduceState("listening", { type: "RESPONSE_READY" })).toBe("listening");
  });

  it("rejects idle to speaking", () => {
    expect(reduceState("idle", { type: "SPEAKING_DONE" })).toBe("idle");
  });

  it("treats listening processing and speaking as busy", () => {
    expect(isBusy("listening")).toBe(true);
    expect(isBusy("processing")).toBe(true);
    expect(isBusy("speaking")).toBe(true);
    expect(isBusy("idle")).toBe(false);
  });

  it("allows barge-in from speaking to listening", () => {
    expect(reduceState("speaking", { type: "START_LISTENING" })).toBe("listening");
    expect(reduceState("processing", { type: "START_LISTENING" })).toBe("listening");
  });
});
