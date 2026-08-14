export function normalizeTranscript(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

export function isUsableTranscript(text: string): boolean {
  return normalizeTranscript(text).length > 0;
}
