export type PlaybackHooks = {
  onStart?: (turnId: string) => void;
  onLevel?: (level: number) => void;
};

export type PlaybackEngine = {
  playWav: (wav: ArrayBuffer, turnId: string, hooks?: PlaybackHooks) => Promise<void>;
  stop: () => void;
  readonly activeTurnId: string | null;
};

type AnalyserLike = {
  fftSize: number;
  smoothingTimeConstant: number;
  getByteTimeDomainData: (data: Uint8Array) => void;
  connect: (node: unknown) => void;
};

type AudioContextCtor = {
  new (): {
    decodeAudioData: (data: ArrayBuffer) => Promise<AudioBuffer>;
    createBufferSource: () => {
      buffer: AudioBuffer | null;
      connect: (node: unknown) => void;
      start: () => void;
      stop: () => void;
      onended: (() => void) | null;
    };
    createAnalyser: () => AnalyserLike;
    destination: unknown;
    close: () => Promise<void>;
    state: string;
    resume: () => Promise<void>;
  };
};

function rms(bytes: Uint8Array): number {
  let sum = 0;
  for (const value of bytes) {
    const centered = (value - 128) / 128;
    sum += centered * centered;
  }
  return Math.sqrt(sum / bytes.length);
}

export function createBrowserPlayback(): PlaybackEngine {
  let context: InstanceType<AudioContextCtor> | null = null;
  let source: ReturnType<InstanceType<AudioContextCtor>["createBufferSource"]> | null = null;
  let activeTurnId: string | null = null;
  let generation = 0;
  let levelFrame = 0;
  let levelHook: PlaybackHooks["onLevel"] | undefined;

  function ensureContext() {
    if (context) {
      return context;
    }
    const Ctor = (globalThis.AudioContext ||
      (globalThis as { webkitAudioContext?: AudioContextCtor }).webkitAudioContext) as
      AudioContextCtor | undefined;
    if (!Ctor) {
      throw new Error("playback_unavailable");
    }
    context = new Ctor();
    return context;
  }

  function clearLevel() {
    if (levelFrame) {
      window.cancelAnimationFrame(levelFrame);
      levelFrame = 0;
    }
    levelHook?.(0);
    levelHook = undefined;
  }

  return {
    get activeTurnId() {
      return activeTurnId;
    },
    stop() {
      generation += 1;
      activeTurnId = null;
      clearLevel();
      try {
        source?.stop();
      } catch {
        /* already stopped */
      }
      source = null;
    },
    async playWav(wav, turnId, hooks) {
      const token = generation;
      activeTurnId = turnId;
      levelHook = hooks?.onLevel;
      const audioContext = ensureContext();
      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }
      if (token !== generation || activeTurnId !== turnId) {
        return;
      }
      const copy = wav.slice(0);
      const buffer = await audioContext.decodeAudioData(copy);
      if (token !== generation || activeTurnId !== turnId) {
        return;
      }
      await new Promise<void>((resolve, reject) => {
        if (token !== generation || activeTurnId !== turnId) {
          resolve();
          return;
        }
        const next = audioContext.createBufferSource();
        next.buffer = buffer;
        try {
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 256;
          analyser.smoothingTimeConstant = 0.55;
          next.connect(analyser);
          analyser.connect(audioContext.destination);
          const samples = new Uint8Array(analyser.fftSize);
          const tick = () => {
            if (token !== generation) {
              return;
            }
            analyser.getByteTimeDomainData(samples);
            levelHook?.(Math.min(1, rms(samples) * 2.6));
            levelFrame = window.requestAnimationFrame(tick);
          };
          levelFrame = window.requestAnimationFrame(tick);
        } catch {
          next.connect(audioContext.destination);
        }
        next.onended = () => {
          if (token === generation) {
            clearLevel();
          }
          if (activeTurnId === turnId) {
            activeTurnId = null;
          }
          resolve();
        };
        source = next;
        try {
          hooks?.onStart?.(turnId);
          next.start();
        } catch (error) {
          clearLevel();
          reject(error);
        }
      });
    },
  };
}

export function createQueuePlayback(engine: PlaybackEngine): PlaybackEngine {
  let queue: Array<{ turnId: string; wav: ArrayBuffer; hooks?: PlaybackHooks }> = [];
  let running = false;
  let activeTurnId: string | null = null;

  async function drain() {
    if (running) {
      return;
    }
    running = true;
    while (queue.length > 0) {
      const item = queue.shift();
      if (!item) {
        break;
      }
      if (item.turnId !== activeTurnId) {
        continue;
      }
      await engine.playWav(item.wav, item.turnId, item.hooks);
    }
    running = false;
  }

  return {
    get activeTurnId() {
      return activeTurnId;
    },
    stop() {
      queue = [];
      activeTurnId = null;
      engine.stop();
    },
    async playWav(wav, turnId, hooks) {
      if (activeTurnId && activeTurnId !== turnId) {
        this.stop();
      }
      activeTurnId = turnId;
      queue.push({ turnId, wav, hooks });
      await drain();
    },
  };
}
