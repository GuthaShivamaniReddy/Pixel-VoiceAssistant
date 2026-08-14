import { describe, expect, it } from "vitest";
import { assertNoSecretShapedPublicEnv, getPublicApiBaseUrl } from "./env";

describe("public env", () => {
  it("provides an API base URL", () => {
    expect(getPublicApiBaseUrl()).toMatch(/^https?:\/\//);
  });

  it("rejects secret-shaped NEXT_PUBLIC keys", () => {
    expect(() =>
      assertNoSecretShapedPublicEnv({
        NEXT_PUBLIC_OPENAI_API_KEY: "sk-test",
      }),
    ).toThrow(/NEXT_PUBLIC_OPENAI_API_KEY/);
  });

  it("allows NEXT_PUBLIC_API_BASE_URL", () => {
    expect(() =>
      assertNoSecretShapedPublicEnv({
        NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8000",
      }),
    ).not.toThrow();
  });
});
