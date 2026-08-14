type AssistantStateIndicatorProps = {
  state: string;
  label: string;
  cancelled: boolean;
};

export function AssistantStateIndicator({ state, label, cancelled }: AssistantStateIndicatorProps) {
  return (
    <p className="state-indicator" data-state={state} role="status" aria-live="polite">
      <span className="state-indicator__badge" aria-hidden="true">
        {state.replaceAll("_", " ")}
      </span>
      <span>{label}</span>
      {cancelled ? <span> Cancelled. Pixel is idle.</span> : null}
    </p>
  );
}
