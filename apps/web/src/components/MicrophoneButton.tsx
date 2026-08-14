type MicrophoneButtonProps = {
  state: string;
  permission: string;
  onStart: () => void;
  disabled: boolean;
};

export function MicrophoneButton({ state, permission, onStart, disabled }: MicrophoneButtonProps) {
  const listening = state === "listening";
  return (
    <button
      type="button"
      className="control"
      onClick={onStart}
      disabled={disabled}
      aria-pressed={listening}
      aria-label={
        listening
          ? "Microphone is on. Pixel is listening."
          : permission === "denied"
            ? "Request microphone access again"
            : state === "speaking"
              ? "Interrupt Pixel and start listening"
              : "Start listening"
      }
    >
      {listening ? "Microphone on" : "Start listening"}
    </button>
  );
}
