export type CaptureHandle = {
  sampleRate: number;
  stop: () => { pcm: Int16Array; sampleRate: number };
};

export type CaptureFactory = {
  start: (stream: MediaStream | null, audioContext?: AudioContext) => Promise<CaptureHandle>;
};

function floatToPcm16(channel: Float32Array): Int16Array {
  const pcm = new Int16Array(channel.length);
  for (let i = 0; i < channel.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, channel[i] ?? 0));
    pcm[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  return pcm;
}

function concatPcm(chunks: Int16Array[]): Int16Array {
  const total = chunks.reduce((sum, part) => sum + part.length, 0);
  const pcm = new Int16Array(total);
  let offset = 0;
  for (const part of chunks) {
    pcm.set(part, offset);
    offset += part.length;
  }
  return pcm;
}

export function createAudioContext(): AudioContext | null {
  const Ctor =
    globalThis.AudioContext ||
    (globalThis as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!Ctor) {
    return null;
  }
  return new Ctor();
}

export function createBrowserCapture(): CaptureFactory {
  return {
    async start(stream, existing) {
      if (!stream) {
        throw new Error("capture_unavailable");
      }
      const context = existing ?? createAudioContext();
      if (!context) {
        throw new Error("capture_unavailable");
      }
      if (context.state === "suspended") {
        await context.resume();
      }
      const chunks: Int16Array[] = [];
      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(4096, 1, 1);
      const mute = context.createGain();
      mute.gain.value = 0;
      processor.onaudioprocess = (event) => {
        chunks.push(floatToPcm16(event.inputBuffer.getChannelData(0)));
      };
      source.connect(processor);
      processor.connect(mute);
      mute.connect(context.destination);
      return {
        sampleRate: context.sampleRate,
        stop() {
          processor.onaudioprocess = null;
          source.disconnect();
          processor.disconnect();
          mute.disconnect();
          void context.close();
          return { pcm: concatPcm(chunks), sampleRate: context.sampleRate };
        },
      };
    },
  };
}
