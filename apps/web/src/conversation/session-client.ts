import { getPublicApiBaseUrl } from "@/lib/env";

export type SessionInfo = {
  sessionId: string;
};

export type SessionClient = {
  create: () => Promise<SessionInfo>;
  clear: (sessionId: string) => Promise<void>;
};

export function createHttpSessionClient(): SessionClient {
  return {
    async create() {
      const response = await fetch(`${getPublicApiBaseUrl()}/v1/sessions`, {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error("session_create_failed");
      }
      const body = (await response.json()) as { session_id?: string };
      return { sessionId: String(body.session_id ?? "") };
    },
    async clear(sessionId: string) {
      const response = await fetch(`${getPublicApiBaseUrl()}/v1/sessions/${sessionId}/clear`, {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      if (response.status === 404 || response.status === 410) {
        return;
      }
      if (!response.ok) {
        throw new Error("session_clear_failed");
      }
    },
  };
}
