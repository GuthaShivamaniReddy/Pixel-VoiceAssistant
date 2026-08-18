import { ControlIcon } from "./ControlIcon";

type MuteControlProps = {
  muted: boolean;
  onToggle: () => void;
};

export function MuteControl({ muted, onToggle }: MuteControlProps) {
  return (
    <button
      type="button"
      className={`control${muted ? " control--danger" : " control--quiet"}`}
      onClick={onToggle}
      aria-pressed={muted}
      aria-label={muted ? "Unmute speech playback" : "Mute speech playback"}
    >
      <ControlIcon name={muted ? "mute" : "unmute"} />
      {muted ? "Muted" : "Voice on"}
    </button>
  );
}
