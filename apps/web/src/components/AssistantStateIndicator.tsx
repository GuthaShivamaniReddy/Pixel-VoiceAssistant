type AssistantStateIndicatorProps = {
  state: string;
  label: string;
  cancelled: boolean;
};

export function AssistantStateIndicator({ state, label, cancelled }: AssistantStateIndicatorProps) {
  const badge =
    state === "idle"
      ? "Ready"
      : state === "permission_denied"
        ? "Mic blocked"
        : state.replaceAll("_", " ");
  return (
    <p className="state-indicator" data-state={state} role="status" aria-live="polite">
      <span className="state-indicator__badge" aria-hidden="true">
        {badge}
      </span>
      <span>{label}</span>
      {cancelled ? <span> Cancelled. Pixel is ready.</span> : null}
    </p>
  );
}
