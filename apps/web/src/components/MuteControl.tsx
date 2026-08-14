type MuteControlProps = {
  muted: boolean;
  onToggle: () => void;
};

export function MuteControl({ muted, onToggle }: MuteControlProps) {
  return (
    <button
      type="button"
      className="control"
      onClick={onToggle}
      aria-pressed={muted}
      aria-label={muted ? "Unmute speech playback" : "Mute speech playback"}
    >
      {muted ? "Muted" : "Unmuted"}
    </button>
  );
}
