import type { PixelMascotState } from "@/mascot/states";
import { PixelCharacter } from "@/mascot/PixelCharacter";
import "@/mascot/mascot.css";

type PixelMiniAvatarProps = {
  state?: Extract<PixelMascotState, "idle" | "speaking" | "warning" | "reading">;
};

export function PixelMiniAvatar({ state = "idle" }: PixelMiniAvatarProps) {
  return (
    <span
      className="pixel-mascot pixel-mini"
      data-state={state}
      data-size="mini"
      data-reduced="true"
      aria-hidden="true"
    >
      <span className="pixel-mascot__stage">
        <PixelCharacter compact />
      </span>
    </span>
  );
}
