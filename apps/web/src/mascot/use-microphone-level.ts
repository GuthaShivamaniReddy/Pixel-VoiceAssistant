"use client";

import { useEffect, useRef } from "react";

function rms(bytes: Uint8Array): number {
  let sum = 0;
  for (const value of bytes) {
    const centered = (value - 128) / 128;
    sum += centered * centered;
  }
  return Math.sqrt(sum / bytes.length);
}

/**
 * Writes a 0–1 mic level to the mascot via CSS, without React state on every frame.
 */
export function useMicrophoneLevel(
  active: boolean,
  stream: MediaStream | null,
  onLevel?: (level: number) => void,
): void {
  const onLevelRef = useRef(onLevel);

  useEffect(() => {
    onLevelRef.current = onLevel;
  }, [onLevel]);

  useEffect(() => {
    if (!active || !stream) {
      onLevelRef.current?.(0);
      return;
    }
    const AudioContextCtor =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AudioContextCtor) {
      return;
    }
    const context = new AudioContextCtor();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.7;
    source.connect(analyser);
    const samples = new Uint8Array(analyser.fftSize);
    let frame = 0;
    let last = -1;

    const tick = () => {
      analyser.getByteTimeDomainData(samples);
      const next = Math.min(1, rms(samples) * 2.4);
      if (Math.abs(next - last) >= 0.04) {
        last = next;
        onLevelRef.current?.(next);
      }
      frame = window.requestAnimationFrame(tick);
    };
    frame = window.requestAnimationFrame(tick);

    return () => {
      window.cancelAnimationFrame(frame);
      source.disconnect();
      void context.close();
      onLevelRef.current?.(0);
    };
  }, [active, stream]);
}
