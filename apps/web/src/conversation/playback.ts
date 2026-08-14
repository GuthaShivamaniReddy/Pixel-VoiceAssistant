export type PlaybackEngine = {
  playWav: (wav: ArrayBuffer, turnId: string) => Promise<void>;
  stop: () => void;
  readonly activeTurnId: string | null;
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
    destination: unknown;
    close: () => Promise<void>;
    state: string;
    resume: () => Promise<void>;
  };
};

export function createBrowserPlayback(): PlaybackEngine {
  let context: InstanceType<AudioContextCtor> | null = null;
  let source: ReturnType<InstanceType<AudioContextCtor>["createBufferSource"]> | null = null;
  let activeTurnId: string | null = null;
  let generation = 0;

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

  return {
    get activeTurnId() {
      return activeTurnId;
    },
    stop() {
      generation += 1;
      activeTurnId = null;
      try {
        source?.stop();
      } catch {
        /* already stopped */
      }
      source = null;
    },
    async playWav(wav, turnId) {
      const token = generation;
      activeTurnId = turnId;
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
        next.connect(audioContext.destination);
        next.onended = () => {
          if (activeTurnId === turnId) {
            activeTurnId = null;
          }
          resolve();
        };
        source = next;
        try {
          next.start();
        } catch (error) {
          reject(error);
        }
      });
    },
  };
}

export function createQueuePlayback(engine: PlaybackEngine): PlaybackEngine {
  let queue: Array<{ turnId: string; wav: ArrayBuffer }> = [];
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
      await engine.playWav(item.wav, item.turnId);
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
    async playWav(wav, turnId) {
      if (activeTurnId && activeTurnId !== turnId) {
        this.stop();
      }
      activeTurnId = turnId;
      queue.push({ turnId, wav });
      await drain();
    },
  };
}
