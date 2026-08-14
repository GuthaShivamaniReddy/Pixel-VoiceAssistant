import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SourceCard } from "./SourceCard";
import { RecommendedAction } from "./RecommendedAction";
import { AssistantStateIndicator } from "./AssistantStateIndicator";
import { MuteControl } from "./MuteControl";

describe("conversation components", () => {
  it("renders a mock source card with an accessible link", () => {
    render(
      <SourceCard
        source={{
          title: "About Cyber Florida",
          name: "Cyber Florida",
          url: "https://cyberflorida.org/about/",
          description: "Public overview",
          provenance: "mock",
        }}
      />,
    );
    expect(screen.getByText(/not live RAG/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /cyber florida: about cyber florida/i }),
    ).toHaveAttribute("href", "https://cyberflorida.org/about/");
  });

  it("labels retrieved sources as approved Cyber Florida pages", () => {
    render(
      <SourceCard
        source={{
          title: "FirstLine",
          name: "Cyber Florida",
          url: "https://cyberflorida.org/firstline/",
          description: "Public-sector training",
          provenance: "retrieval",
        }}
      />,
    );
    expect(screen.getByText(/Approved Cyber Florida source/i)).toBeInTheDocument();
  });

  it("does not render off-allowlist source URLs as links", () => {
    render(
      <SourceCard
        source={{
          title: "Unsafe",
          name: "Blocked",
          url: "javascript:alert(1)",
          description: "Should not be clickable",
          provenance: "mock",
        }}
      />,
    );
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.getByText(/link blocked/i)).toBeInTheDocument();
  });

  it("renders a recommended action as a named link", () => {
    render(
      <RecommendedAction
        action={{ id: "learn", label: "Learn more", href: "https://cyberflorida.org/" }}
      />,
    );
    expect(
      screen.getByRole("link", { name: /learn more \(opens in a new tab\)/i }),
    ).toBeInTheDocument();
  });

  it("shows state as text, not color alone", () => {
    render(
      <AssistantStateIndicator
        state="listening"
        label="Listening — microphone is on"
        cancelled={false}
      />,
    );
    expect(screen.getByRole("status")).toHaveTextContent(/listening/i);
    expect(screen.getByRole("status")).toHaveTextContent(/microphone is on/i);
  });

  it("exposes mute as a labeled pressed button", () => {
    let muted = false;
    const view = render(<MuteControl muted={muted} onToggle={() => undefined} />);
    expect(screen.getByRole("button", { name: /mute speech playback/i })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    muted = true;
    view.rerender(<MuteControl muted={muted} onToggle={() => undefined} />);
    expect(screen.getByRole("button", { name: /unmute speech playback/i })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: /unmute speech playback/i })).toHaveTextContent(
      "Muted",
    );
  });
});
