import type { RecommendedAction as Action } from "@/conversation/types";
import { isAllowlistedHref } from "@/conversation/allowlist";

type RecommendedActionProps = {
  action: Action;
};

export function RecommendedAction({ action }: RecommendedActionProps) {
  if (!isAllowlistedHref(action.href)) {
    return (
      <span className="action-chip action-chip--blocked">
        {action.label} (blocked — not an approved Cyber Florida URL)
      </span>
    );
  }
  return (
    <a
      className="action-chip"
      href={action.href}
      rel="noreferrer noopener"
      target="_blank"
      aria-label={`${action.label} (opens in a new tab)`}
    >
      {action.label}
    </a>
  );
}
