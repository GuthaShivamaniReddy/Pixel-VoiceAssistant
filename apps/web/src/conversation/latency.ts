export type LatencyMetrics = {
  time_to_transcript_ms: number | null;
  model_latency_ms: number | null;
  tts_latency_ms: number | null;
  time_to_first_audio_ms: number | null;
  total_turn_latency_ms: number | null;
  retrieval_latency_ms: number | null;
};

export const EMPTY_METRICS: LatencyMetrics = {
  time_to_transcript_ms: null,
  model_latency_ms: null,
  tts_latency_ms: null,
  time_to_first_audio_ms: null,
  total_turn_latency_ms: null,
  retrieval_latency_ms: null,
};
