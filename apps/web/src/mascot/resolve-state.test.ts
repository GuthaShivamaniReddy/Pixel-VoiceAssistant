import { describe, expect, it } from "vitest";
import { resolvePixelMascotState, type PixelMascotInput } from "./resolve-state";

const base: PixelMascotInput = {
  assistantState: "idle",
  muted: false,
  errorCode: null,
  hasConversation: false,
  cue: "none",
  retrievalActive: false,
  toolActive: false,
  speakingHasSources: false,
  speakingHasActions: false,
};

describe("resolvePixelMascotState", () => {
  it("maps assistant idle to mascot idle", () => {
    expect(resolvePixelMascotState(base)).toBe("idle");
  });

  it("maps listening to listening", () => {
    expect(resolvePixelMascotState({ ...base, assistantState: "listening" })).toBe("listening");
  });

  it("does not show listening unless the mic state is listening", () => {
    expect(resolvePixelMascotState({ ...base, assistantState: "processing" })).toBe("thinking");
    expect(resolvePixelMascotState({ ...base, assistantState: "speaking" })).toBe("speaking");
  });

  it("maps processing to thinking unless retrieval or tool is actually active", () => {
    expect(resolvePixelMascotState({ ...base, assistantState: "processing" })).toBe("thinking");
    expect(
      resolvePixelMascotState({ ...base, assistantState: "processing", retrievalActive: true }),
    ).toBe("searching");
    expect(
      resolvePixelMascotState({ ...base, assistantState: "processing", toolActive: true }),
    ).toBe("toolAction");
  });

  it("does not search while idle even if a previous turn had sources", () => {
    expect(
      resolvePixelMascotState({ ...base, speakingHasSources: true, retrievalActive: false }),
    ).toBe("idle");
  });

  it("maps speaking to speaking, reading, or navigation from real extras", () => {
    expect(resolvePixelMascotState({ ...base, assistantState: "speaking" })).toBe("speaking");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "speaking",
        speakingHasSources: true,
      }),
    ).toBe("reading");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "speaking",
        speakingHasActions: true,
        speakingHasSources: true,
      }),
    ).toBe("toolAction");
  });

  it("stops speaking immediately when barge-in starts listening", () => {
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "listening",
        speakingHasSources: true,
        cue: "success",
      }),
    ).toBe("listening");
  });

  it("maps network errors to offline and other errors to error", () => {
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "error",
        errorCode: "network",
      }),
    ).toBe("offline");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "error",
        errorCode: "response_failure",
      }),
    ).toBe("error");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "permission_denied",
        errorCode: "permission_denied",
      }),
    ).toBe("error");
  });

  it("shows muted only when idle and not in a higher-priority state", () => {
    expect(resolvePixelMascotState({ ...base, muted: true })).toBe("muted");
    expect(resolvePixelMascotState({ ...base, assistantState: "listening", muted: true })).toBe(
      "listening",
    );
  });

  it("plays greeting once on an empty idle session", () => {
    expect(resolvePixelMascotState({ ...base, cue: "greeting" })).toBe("greeting");
    expect(resolvePixelMascotState({ ...base, cue: "greeting", hasConversation: true })).toBe(
      "idle",
    );
  });

  it("applies short idle cues without overriding live work", () => {
    expect(resolvePixelMascotState({ ...base, cue: "success" })).toBe("success");
    expect(resolvePixelMascotState({ ...base, cue: "clearing" })).toBe("clearing");
    expect(resolvePixelMascotState({ ...base, cue: "recovering" })).toBe("recovering");
    expect(resolvePixelMascotState({ ...base, cue: "uncertain" })).toBe("uncertain");
    expect(resolvePixelMascotState({ ...base, cue: "warning" })).toBe("warning");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "processing",
        cue: "recovering",
      }),
    ).toBe("thinking");
    expect(
      resolvePixelMascotState({
        ...base,
        assistantState: "processing",
        cue: "success",
      }),
    ).toBe("thinking");
  });
});
