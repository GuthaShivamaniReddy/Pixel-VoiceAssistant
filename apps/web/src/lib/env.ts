const FORBIDDEN = ["SECRET", "API_KEY", "TOKEN", "PASSWORD", "PRIVATE"] as const;

export function getPublicApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
}

export function assertNoSecretShapedPublicEnv(
  env: Record<string, string | undefined> = process.env,
): void {
  for (const key of Object.keys(env)) {
    if (!key.startsWith("NEXT_PUBLIC_")) {
      continue;
    }
    const upper = key.toUpperCase();
    if (FORBIDDEN.some((part) => upper.includes(part))) {
      throw new Error(`Refusing secret-shaped public env var: ${key}`);
    }
  }
}
