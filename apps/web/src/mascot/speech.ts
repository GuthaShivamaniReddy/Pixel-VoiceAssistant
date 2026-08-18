export type PixelMouth = "silence" | "low" | "medium" | "high";
export type PixelSpeakGesture = "explain" | "point" | "security" | "recommend";

export function mouthFromLevel(level: number): PixelMouth {
  if (level < 0.12) {
    return "silence";
  }
  if (level < 0.32) {
    return "low";
  }
  if (level < 0.6) {
    return "medium";
  }
  return "high";
}

export function speakGestureForTurn(input: {
  text: string;
  sources: unknown[];
  actions: unknown[];
}): PixelSpeakGesture {
  if (input.actions.length > 0) {
    return "point";
  }
  if (/phish|scam|suspicious|password|compromis|don't click|do not click/i.test(input.text)) {
    return "security";
  }
  if (input.sources.length > 0) {
    return "recommend";
  }
  return "explain";
}
