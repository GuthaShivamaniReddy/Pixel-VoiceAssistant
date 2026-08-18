import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MASCOT_CAPTION, PIXEL_MASCOT_STATES } from "@/mascot/states";
import { PixelMascot } from "./PixelMascot";

describe("PixelMascot", () => {
  it.each(["idle", "listening", "thinking", "speaking", "error"] as const)(
    "renders %s from supplied state",
    (state) => {
      render(<PixelMascot state={state} />);
      expect(document.querySelector(`[data-state="${state}"]`)).toBeTruthy();
      expect(screen.getByText(MASCOT_CAPTION[state])).toBeInTheDocument();
    },
  );

  it("uses the original SVG Pixel character, not the reference photo", () => {
    render(<PixelMascot state="idle" />);
    expect(document.querySelector("svg.pixel-char")).toBeTruthy();
    expect(document.querySelector("svg.pixel-stage")).toBeTruthy();
    expect(document.querySelector(".pixel-char__head")).toBeTruthy();
    expect(document.querySelector(".pixel-char__antenna--left")).toBeTruthy();
    expect(document.querySelector(".pixel-char__arm--right")).toBeTruthy();
    expect(document.querySelector(".pixel-char__leg--left")).toBeTruthy();
    expect(document.querySelector(".pixel-face--idle")).toBeTruthy();
    expect(document.querySelector("img")).toBeNull();
    expect(document.querySelector('image[href*="pixel-mascot.png"]')).toBeNull();
  });

  it("keeps the mascot decorative and does not fake searching from idle", () => {
    render(<PixelMascot state="idle" />);
    expect(document.querySelector(".pixel-mascot")).toHaveAttribute("aria-hidden", "true");
    expect(screen.queryByText(MASCOT_CAPTION.searching)).not.toBeInTheDocument();
  });

  it("covers every typed mascot state caption", () => {
    for (const state of PIXEL_MASCOT_STATES) {
      const view = render(<PixelMascot state={state} />);
      expect(screen.getByText(MASCOT_CAPTION[state])).toBeInTheDocument();
      view.unmount();
    }
  });

  it("uses a compact head-only sprite for transcript-sized Pixel", () => {
    render(<PixelMascot state="idle" size="mini" showCaption={false} />);
    expect(document.querySelector("svg.pixel-stage")).toBeNull();
    expect(document.querySelector(".pixel-char--compact")).toBeTruthy();
    expect(document.querySelector(".pixel-char__leg--left")).toBeNull();
  });

  it("sets reduced-motion from prefers-reduced-motion", async () => {
    const previous = window.matchMedia;
    window.matchMedia = (query: string) =>
      ({
        matches: query.includes("prefers-reduced-motion"),
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }) as unknown as MediaQueryList;
    try {
      render(<PixelMascot state="listening" />);
      await waitFor(() => {
        expect(document.querySelector(".pixel-mascot")).toHaveAttribute("data-reduced", "true");
      });
    } finally {
      window.matchMedia = previous;
    }
  });
});
