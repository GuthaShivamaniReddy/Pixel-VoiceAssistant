import type { MicPermission } from "./types";

export type MicrophoneBridge = {
  requestAccess: () => Promise<Exclude<MicPermission, "unknown">>;
  getStream: () => MediaStream | null;
  release: () => void;
};

function isDenied(error: unknown): boolean {
  if (!error || typeof error !== "object") {
    return false;
  }
  const name = "name" in error ? String(error.name) : "";
  return name === "NotAllowedError" || name === "PermissionDeniedError" || name === "SecurityError";
}

export function createBrowserMicrophone(): MicrophoneBridge {
  let stream: MediaStream | null = null;

  return {
    async requestAccess() {
      if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
        return "unavailable";
      }
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach((track) => {
          track.addEventListener("ended", () => {
            if (stream) {
              stream.getTracks().forEach((open) => open.stop());
              stream = null;
            }
          });
        });
        return "granted";
      } catch (error) {
        if (isDenied(error)) {
          return "denied";
        }
        return "unavailable";
      }
    },
    release() {
      stream?.getTracks().forEach((track) => track.stop());
      stream = null;
    },
    getStream() {
      return stream;
    },
  };
}

export function createStubMicrophone(
  result: Exclude<MicPermission, "unknown"> = "granted",
): MicrophoneBridge {
  return {
    requestAccess: async () => result,
    getStream: () => null,
    release() {
      /* no tracks in tests */
    },
  };
}
