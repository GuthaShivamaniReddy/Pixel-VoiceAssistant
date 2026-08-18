import { describe, expect, it } from "vitest";
import { mouthFromLevel, speakGestureForTurn } from "./speech";

describe("speech mouth and gesture mapping", () => {
  it("maps amplitude to closed/open mouth bands", () => {
    expect(mouthFromLevel(0)).toBe("silence");
    expect(mouthFromLevel(0.2)).toBe("low");
    expect(mouthFromLevel(0.5)).toBe("medium");
    expect(mouthFromLevel(0.9)).toBe("high");
  });

  it("points for tools and stays calm for security guidance", () => {
    expect(
      speakGestureForTurn({
        text: "I added the official resource on screen.",
        sources: [],
        actions: [{ id: "open" }],
      }),
    ).toBe("point");
    expect(
      speakGestureForTurn({
        text: "That message has several common phishing indicators. Do not click the link.",
        sources: [],
        actions: [],
      }),
    ).toBe("security");
  });
});
