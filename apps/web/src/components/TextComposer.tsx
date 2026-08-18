import type { RefObject } from "react";

import { ControlIcon } from "./ControlIcon";

type TextComposerProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
  inputRef?: RefObject<HTMLTextAreaElement | null>;
};

export function TextComposer({ value, onChange, onSubmit, disabled, inputRef }: TextComposerProps) {
  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label htmlFor="pixel-message">Message Pixel</label>
      <div className="composer__row">
        <textarea
          id="pixel-message"
          name="message"
          ref={inputRef}
          rows={3}
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          onInput={(event) => onChange(event.currentTarget.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSubmit();
            }
          }}
          placeholder="Ask about Cyber Florida or defensive cybersecurity. Enter to send."
        />
        <button
          type="submit"
          className="control control--primary"
          disabled={disabled || !value.trim()}
        >
          <ControlIcon name="send" />
          Send
        </button>
      </div>
    </form>
  );
}
