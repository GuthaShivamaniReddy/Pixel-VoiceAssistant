import { describe, expect, it } from "vitest";
import { isUsableTranscript, normalizeTranscript } from "./normalize";

describe("transcript normalization", () => {
  it("trims and collapses whitespace", () => {
    expect(normalizeTranscript("  What   is  Pixel \n")).toBe("What is Pixel");
  });

  it("rejects empty and whitespace-only transcripts", () => {
    expect(isUsableTranscript("")).toBe(false);
    expect(isUsableTranscript("   ")).toBe(false);
    expect(isUsableTranscript("hello")).toBe(true);
  });
});
