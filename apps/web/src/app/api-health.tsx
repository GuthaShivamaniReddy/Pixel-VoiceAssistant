"use client";

import { useEffect, useState } from "react";
import { getPublicApiBaseUrl } from "@/lib/env";

type Health = { status?: string; service?: string; env?: string };

export function ApiHealth() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  const base = getPublicApiBaseUrl();

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${base}/health`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Health check failed (${response.status})`);
        }
        return (await response.json()) as Health;
      })
      .then(setHealth)
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setError(err instanceof Error ? err.message : "Health check failed");
      });
    return () => controller.abort();
  }, [base]);

  if (error) {
    return (
      <p role="status">
        API health: unavailable ({error}). Start the API on {base}.
      </p>
    );
  }
  if (!health) {
    return <p role="status">Checking API health…</p>;
  }
  return (
    <p role="status">
      API health: {health.status} ({health.service}, env={health.env})
    </p>
  );
}
