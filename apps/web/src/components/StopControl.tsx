type StopControlProps = {
  state: string;
  onStopListening: () => void;
  onStopSpeaking: () => void;
};

export function StopControl({ state, onStopListening, onStopSpeaking }: StopControlProps) {
  const listening = state === "listening";
  const speaking = state === "speaking";
  const enabled = listening || speaking;
  return (
    <button
      type="button"
      className="control"
      disabled={!enabled}
      onClick={listening ? onStopListening : onStopSpeaking}
      aria-label={
        listening
          ? "Stop listening and send the sample question"
          : speaking
            ? "Stop Pixel speaking"
            : "Stop unavailable"
      }
    >
      Stop
    </button>
  );
}
