"use client";

import { forwardRef } from "react";
import { MASCOT_CAPTION, type PixelMascotSize, type PixelMascotState } from "@/mascot/states";
import { PixelCharacter } from "@/mascot/PixelCharacter";
import { PixelStage } from "@/mascot/PixelStage";
import type { PixelSpeakGesture } from "@/mascot/speech";
import { usePrefersReducedMotion } from "@/mascot/use-reduced-motion";
import "@/mascot/mascot.css";

type PixelMascotProps = {
  state: PixelMascotState;
  size?: PixelMascotSize;
  showCaption?: boolean;
  gesture?: PixelSpeakGesture;
};

export const PixelMascot = forwardRef<HTMLElement, PixelMascotProps>(function PixelMascot(
  { state, size = "stage", showCaption = true, gesture = "explain" },
  ref,
) {
  const reducedMotion = usePrefersReducedMotion();

  return (
    <figure
      ref={ref}
      className="pixel-mascot"
      data-state={state}
      data-size={size}
      data-gesture={gesture}
      data-reduced={reducedMotion ? "true" : "false"}
      aria-hidden="true"
    >
      <div className="pixel-mascot__stage">
        {size !== "mini" ? <PixelStage /> : null}
        <div className="pixel-mascot__sprite-wrap">
          <div className="pixel-mascot__actor">
            <PixelCharacter compact={size === "mini"} />
          </div>
        </div>
      </div>
      {showCaption ? (
        <figcaption className="pixel-mascot__caption">{MASCOT_CAPTION[state]}</figcaption>
      ) : null}
    </figure>
  );
});
