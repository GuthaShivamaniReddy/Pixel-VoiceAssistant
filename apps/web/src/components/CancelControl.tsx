type CancelControlProps = {
  enabled: boolean;
  onCancel: () => void;
};

export function CancelControl({ enabled, onCancel }: CancelControlProps) {
  return (
    <button
      type="button"
      className="control"
      disabled={!enabled}
      onClick={onCancel}
      aria-label="Cancel current turn"
    >
      Cancel
    </button>
  );
}
