import { describe, expect, it } from "vitest";
import { isAllowlistedHref } from "./allowlist";

describe("href allowlist", () => {
  it("allows Cyber Florida https URLs", () => {
    expect(isAllowlistedHref("https://cyberflorida.org/about/")).toBe(true);
    expect(isAllowlistedHref("https://www.cyberflorida.org/")).toBe(true);
  });

  it("rejects javascript, http, and off-host URLs", () => {
    expect(isAllowlistedHref("javascript:alert(1)")).toBe(false);
    expect(isAllowlistedHref("http://cyberflorida.org/")).toBe(false);
    expect(isAllowlistedHref("https://cyberflorida.org.evil.example/")).toBe(false);
    expect(isAllowlistedHref("https://example.com/")).toBe(false);
  });
});
