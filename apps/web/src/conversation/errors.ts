import type { ErrorCode } from "./types";

export const ERROR_COPY: Record<ErrorCode, { title: string; detail: string }> = {
  permission_denied: {
    title: "Microphone blocked",
    detail:
      "Pixel needs microphone access only while you choose to speak. You can keep using text, or allow the microphone in the browser and try again.",
  },
  mic_unavailable: {
    title: "Microphone unavailable",
    detail: "This device or browser cannot open a microphone. Use text input instead.",
  },
  network: {
    title: "Connection problem",
    detail: "Pixel could not complete that request. Try again, or type your question.",
  },
  response_failure: {
    title: "Reply failed",
    detail: "Pixel could not finish that answer. Try again, or ask a different question.",
  },
  timeout: {
    title: "Taking too long",
    detail: "That request timed out. Try again, or use a shorter question.",
  },
  empty: {
    title: "No reply",
    detail: "Pixel had nothing to say for that turn. Try another question.",
  },
  generic: {
    title: "Something went wrong",
    detail: "Pixel hit a problem. You can try again or return to idle and use text.",
  },
  stt_failure: {
    title: "Could not transcribe",
    detail: "Pixel could not convert that speech to text. Try again, or type your question.",
  },
  tts_failure: {
    title: "Voice playback failed",
    detail: "The written reply is on screen. You can keep using text, or try voice again.",
  },
  playback_failure: {
    title: "Could not play audio",
    detail: "The reply is on screen. Check your speakers, or continue with text.",
  },
  capture_failure: {
    title: "Microphone capture failed",
    detail: "Pixel could not record audio. Check the microphone, or type instead.",
  },
};
