import { ControlIcon } from "./ControlIcon";

type CancelControlProps = {
  enabled: boolean;
  onCancel: () => void;
};

export function CancelControl({ enabled, onCancel }: CancelControlProps) {
  return (
    <button
      type="button"
      className="control control--quiet"
      disabled={!enabled}
      onClick={onCancel}
      aria-label="Cancel current turn"
    >
      <ControlIcon name="cancel" />
      Cancel
    </button>
  );
}
