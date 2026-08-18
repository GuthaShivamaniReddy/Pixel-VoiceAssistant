import { ControlIcon } from "./ControlIcon";

type MicrophoneButtonProps = {
  state: string;
  permission: string;
  onStart: () => void;
  disabled: boolean;
};

export function MicrophoneButton({ state, permission, onStart, disabled }: MicrophoneButtonProps) {
  const listening = state === "listening";
  const denied = permission === "denied";
  const unavailable = permission === "unavailable";
  const mic = listening ? "listening" : denied ? "denied" : unavailable ? "unavailable" : "ready";
  const label = listening
    ? "Listening…"
    : denied
      ? "Microphone blocked"
      : unavailable
        ? "Microphone unavailable"
        : state === "speaking"
          ? "Interrupt and listen"
          : "Start listening";
  return (
    <button
      type="button"
      className="control control--mic"
      data-mic={mic}
      onClick={onStart}
      disabled={disabled}
      aria-pressed={listening}
      aria-label={
        listening
          ? "Microphone is on. Pixel is listening."
          : denied
            ? "Request microphone access again"
            : unavailable
              ? "Microphone unavailable"
              : state === "speaking"
                ? "Interrupt Pixel and start listening"
                : "Start listening"
      }
    >
      <ControlIcon name="mic" />
      {label}
    </button>
  );
}
