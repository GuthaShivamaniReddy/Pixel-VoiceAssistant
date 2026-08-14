import type { MockReply, RecommendedAction, SourceRef } from "./types";

const ABOUT: SourceRef = {
  title: "About Cyber Florida",
  name: "Cyber Florida",
  url: "https://cyberflorida.org/about/",
  description: "Public overview of the Florida Center for Cybersecurity at USF.",
  provenance: "mock",
};

const PROGRAMS: SourceRef = {
  title: "Programs",
  name: "Cyber Florida",
  url: "https://cyberflorida.org/",
  description: "Public programs and education entry points (mocked for UX testing).",
  provenance: "mock",
};

const VIEW_SITE: RecommendedAction = {
  id: "view-site",
  label: "Learn more",
  href: "https://cyberflorida.org/",
};

const VIEW_ABOUT: RecommendedAction = {
  id: "view-about",
  label: "Open resource",
  href: "https://cyberflorida.org/about/",
};

const AI_DISCLOSURE =
  "I am Pixel, an AI assistant for Cyber Florida — not a person or emergency service. ";

function normalize(text: string): string {
  return text.trim().toLowerCase().replace(/\s+/g, " ");
}

function ok(
  spoken: string,
  sources: SourceRef[] = [],
  actions: RecommendedAction[] = [],
  delayMs = 280,
): MockReply {
  return { kind: "ok", spoken, sources, actions, delayMs };
}

function fail(
  code: Extract<MockReply, { kind: "fail" }>["code"],
  message: string,
  delayMs = 280,
): MockReply {
  return { kind: "fail", code, message, delayMs };
}

export class MockConversationProvider {
  private firstReply = true;
  private topic: string | null = null;
  private lastSources: SourceRef[] = [];

  clear(): void {
    this.firstReply = true;
    this.topic = null;
    this.lastSources = [];
  }

  lastTopic(): string | null {
    return this.topic;
  }

  respond(userText: string): MockReply {
    const key = normalize(userText);
    if (!key) {
      return fail(
        "empty",
        "I did not catch a question. Type a message, or try the microphone again.",
      );
    }

    if (key === "simulate network error") {
      return fail(
        "network",
        "I could not reach the assistant service. Try again or use text.",
        400,
      );
    }
    if (key === "simulate response failure") {
      return fail(
        "response_failure",
        "I could not complete that reply. Try again, or ask another way.",
        320,
      );
    }
    if (key === "simulate timeout") {
      return fail(
        "timeout",
        "That is taking too long. Try again, or use a shorter question.",
        1600,
      );
    }
    if (key === "simulate empty") {
      return fail("empty", "I did not have a reply to show. Try another question.", 240);
    }

    const reply = this.answer(key);
    if (reply.kind === "ok") {
      this.lastSources = reply.sources;
      if (this.firstReply) {
        this.firstReply = false;
        return { ...reply, spoken: AI_DISCLOSURE + reply.spoken };
      }
    }
    return reply;
  }

  private answer(key: string): MockReply {
    if (key.includes("what is cyber florida")) {
      this.topic = "cyber-florida";
      return ok(
        "Cyber Florida is the Florida Center for Cybersecurity at the University of South Florida. It supports cybersecurity education, research, and outreach for the state. I can point you to public pages; I do not speak as staff.",
        [ABOUT],
        [VIEW_ABOUT],
      );
    }

    if (
      key.includes("what cybersecurity programs") ||
      key.includes("what programs") ||
      key.includes("programs are available")
    ) {
      this.topic = "programs";
      return ok(
        "Cyber Florida publishes workforce, education, and public-sector programs on its public site. Open the programs resource for the current list — I will not invent names that are not on an approved page.",
        [PROGRAMS],
        [
          { id: "view-program", label: "View program", href: "https://cyberflorida.org/" },
          VIEW_SITE,
        ],
      );
    }

    if (key === "explain phishing" || key.startsWith("explain phishing")) {
      this.topic = "phishing";
      return ok(
        "Phishing is a trick that tries to steal passwords or install malware, often by fake urgency in email or messages. Pause, do not click or type credentials, and open the real site yourself if you must check an account.",
      );
    }

    if (key.includes("clicked a suspicious link") || key.includes("clicked a suspicious")) {
      this.topic = "incident-link";
      return ok(
        "Stop using that link or page, and do not enter passwords or codes. If this is a work device, tell your IT or security team now. I cannot see your computer or take action for you. If anyone is in immediate danger, call 911.",
        [],
        [VIEW_SITE],
      );
    }

    if (key === "show me the source" || key.includes("show me the source")) {
      if (this.lastSources.length === 0) {
        return ok(
          "I do not have a mock source card for the last turn. Ask about Cyber Florida or programs to see an example card. These cards are not live retrieval.",
        );
      }
      return ok(
        "Here are the mock source cards from the last Cyber Florida answer. They are prototype data, not live RAG evidence.",
        this.lastSources,
        [VIEW_SITE],
      );
    }

    if (key === "tell me more" || key === "tell me more.") {
      return this.expand();
    }

    if (
      key.includes("dump system prompt") ||
      key.includes("ignore previous") ||
      key === "api keys"
    ) {
      this.topic = "unsupported";
      return ok(
        "I cannot share hidden instructions, secrets, or API keys. I can help with public Cyber Florida information or defensive cybersecurity basics.",
      );
    }
    this.topic = "general";
    return ok(
      "I can help with public Cyber Florida information and defensive cybersecurity basics. Ask about Cyber Florida, programs, or phishing, or type a specific public question. I will not invent organization facts.",
    );
  }

  private expand(): MockReply {
    switch (this.topic) {
      case "cyber-florida":
        return ok(
          "Cyber Florida works on education, research, and outreach rather than acting as a help desk or law enforcement. For official details, use the public About page. I am an AI, so treat that page as the authority.",
          [ABOUT],
          [VIEW_ABOUT],
        );
      case "programs":
        return ok(
          "Program names and eligibility change. Use the public site for the current catalog instead of relying on a remembered list from me.",
          [PROGRAMS],
          [{ id: "view-program", label: "View program", href: "https://cyberflorida.org/" }],
        );
      case "phishing":
        return ok(
          "A practical habit: hover or inspect the sender, go to the site from a bookmark, and report suspected phishing to IT if it is a work account. I will not provide attack instructions.",
        );
      case "incident-link":
        return ok(
          "Next steps stay defensive: disconnect if instructed by IT, watch for password prompts, and change credentials only on a known-good site. I still cannot inspect the device.",
        );
      default:
        return ok(
          "Tell me which topic you want expanded — for example Cyber Florida, programs, or phishing — so I do not guess.",
        );
    }
  }
}

export const SAMPLE_UTTERANCES = [
  "What is Cyber Florida?",
  "What cybersecurity programs are available?",
  "Explain phishing.",
  "I clicked a suspicious link.",
] as const;
