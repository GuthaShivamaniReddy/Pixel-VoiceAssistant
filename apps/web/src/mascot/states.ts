export const PIXEL_MASCOT_STATES = [
  "idle",
  "greeting",
  "listening",
  "thinking",
  "searching",
  "reading",
  "speaking",
  "toolAction",
  "success",
  "warning",
  "uncertain",
  "error",
  "offline",
  "muted",
  "goodbye",
  "clearing",
  "recovering",
] as const;

export type PixelMascotState = (typeof PIXEL_MASCOT_STATES)[number];

export type PixelMascotSize = "hero" | "stage" | "mini";

export type PixelMascotCue =
  "none" | "greeting" | "success" | "clearing" | "uncertain" | "warning" | "recovering";

export const MASCOT_CAPTION: Record<PixelMascotState, string> = {
  idle: "Ready",
  greeting: "Hello",
  listening: "Listening…",
  thinking: "Thinking",
  searching: "Searching Cyber Florida",
  reading: "Using approved sources",
  speaking: "Speaking",
  toolAction: "Opening an approved resource",
  success: "Done",
  warning: "Security guidance",
  uncertain: "Cannot verify from approved sources",
  error: "Something went wrong",
  offline: "Connection lost",
  muted: "Voice muted",
  goodbye: "Goodbye",
  clearing: "Conversation cleared",
  recovering: "Retrying",
};
