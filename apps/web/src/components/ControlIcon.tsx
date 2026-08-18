type IconName = "mic" | "stop" | "mute" | "unmute" | "cancel" | "send" | "clear" | "retry";

const PATHS: Record<IconName, string> = {
  mic: "M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zm-7 9a7 7 0 0 0 14 0M12 19v3",
  stop: "M7 7h10v10H7z",
  mute: "M5 9v6h4l5 4V5L9 9H5zm12.5 3 3 3m0-6-3 3",
  unmute: "M5 9v6h4l5 4V5L9 9H5zm11 1.5a3.5 3.5 0 0 1 0 5",
  cancel: "M6 6l12 12M18 6 6 18",
  send: "M4 12h14M13 6l7 6-7 6",
  clear: "M5 7h14M9 7V5h6v2m-8 0 1 12h8l1-12",
  retry: "M5 12a7 7 0 1 0 2-4.9M5 5v5h5",
};

export function ControlIcon({ name }: { name: IconName }) {
  return (
    <svg className="control__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path
        d={PATHS[name]}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
