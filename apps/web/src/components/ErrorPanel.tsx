type ErrorPanelProps = {
  title: string;
  detail: string;
  onRetry: () => void;
  onIdle: () => void;
  onFocusText: () => void;
};

export function ErrorPanel({ title, detail, onRetry, onIdle, onFocusText }: ErrorPanelProps) {
  return (
    <div className="error-panel" role="alert">
      <h2>{title}</h2>
      <p>{detail}</p>
      <div className="controls">
        <button type="button" className="control control--primary" onClick={onRetry}>
          Try again
        </button>
        <button type="button" className="control" onClick={onFocusText}>
          Use text instead
        </button>
        <button type="button" className="control" onClick={onIdle}>
          Return to idle
        </button>
      </div>
    </div>
  );
}
