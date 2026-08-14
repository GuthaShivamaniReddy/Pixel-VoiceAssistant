export type Scheduler = {
  wait: (ms: number, callback: () => void) => () => void;
};

export function createBrowserScheduler(): Scheduler {
  return {
    wait(ms, callback) {
      const id = setTimeout(callback, ms);
      return () => clearTimeout(id);
    },
  };
}

export function createManualScheduler(): Scheduler & { flush: () => void } {
  const pending: Array<() => void> = [];
  return {
    wait(_ms, callback) {
      pending.push(callback);
      return () => {
        const index = pending.indexOf(callback);
        if (index >= 0) {
          pending.splice(index, 1);
        }
      };
    },
    flush() {
      const jobs = pending.splice(0);
      for (const job of jobs) {
        job();
      }
    },
  };
}
