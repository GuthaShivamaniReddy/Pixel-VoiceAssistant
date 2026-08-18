import { ControlIcon } from "./ControlIcon";

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
      <p className="error-panel__label">What happened</p>
      <h2>{title}</h2>
      <p className="error-panel__label">What you can do</p>
      <p>{detail}</p>
      <div className="controls">
        <button type="button" className="control control--primary" onClick={onRetry}>
          <ControlIcon name="retry" />
          Try again
        </button>
        <button type="button" className="control" onClick={onFocusText}>
          Use text
        </button>
        <button type="button" className="control control--quiet" onClick={onIdle}>
          Return to ready
        </button>
      </div>
    </div>
  );
}
