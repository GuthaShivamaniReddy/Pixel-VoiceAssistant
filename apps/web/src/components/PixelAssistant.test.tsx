import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { PixelAssistant } from "./PixelAssistant";

describe("PixelAssistant labels", () => {
  it("exposes core controls with accessible names", () => {
    render(<PixelAssistant />);
    expect(screen.getByRole("button", { name: /start listening/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /mute speech playback/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel current turn/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /clear conversation/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/message pixel/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^send$/i })).toBeInTheDocument();
    expect(screen.getByText(/not listening until you start/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /meet pixel/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /what is cyber florida\?/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /skip to message pixel/i })).toBeInTheDocument();
    expect(document.querySelector(".pixel-mascot")).toHaveAttribute("aria-hidden", "true");
  });

  it("keeps send disabled for empty text", async () => {
    const user = userEvent.setup();
    render(<PixelAssistant />);
    const send = screen.getByRole("button", { name: /^send$/i });
    expect(send).toBeDisabled();
    await user.type(screen.getByLabelText(/message pixel/i), "Explain phishing.");
    expect(send).toBeEnabled();
  });
});
