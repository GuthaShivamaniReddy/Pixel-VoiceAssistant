from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from pixel.ai import ChatMessage
from pixel.domain import action_to_dict, source_to_dict
from pixel.orchestrator.catalog import ABOUT, HOME, OPEN_ABOUT, OPEN_HOME
from pixel.orchestrator.fallbacks import INJECTION_REFUSAL

AI_DISCLOSURE = (
    "I am Pixel, an AI assistant for Cyber Florida — not a person or emergency service. "
)


@dataclass
class SafeReply:
    text: str
    sources: list[dict[str, str]] = field(default_factory=list)
    actions: list[dict[str, str]] = field(default_factory=list)
    error_code: str | None = None


def _history_blob(history: Sequence[ChatMessage]) -> str:
    return " ".join(message.content.lower() for message in history)


class SafeReplySession:
    """Deterministic replies for the mock LLM. Topic comes from history, not hidden memory."""

    def respond(self, user_text: str, history: Sequence[ChatMessage] = ()) -> SafeReply:
        key = " ".join(user_text.strip().lower().split())
        if not key:
            return SafeReply(
                text="I did not catch a question. Type a message, or try the microphone again.",
                error_code="empty",
            )
        simulated = self._simulated(key)
        if simulated is not None:
            return simulated
        reply = self._answer(key, history)
        if reply.error_code is None and not any(item.role == "assistant" for item in history):
            reply.text = AI_DISCLOSURE + reply.text
        return reply

    def _simulated(self, key: str) -> SafeReply | None:
        if key == "simulate network error":
            return SafeReply(
                text="I could not reach the assistant service. Try again or use text.",
                error_code="network",
            )
        if key == "simulate response failure":
            return SafeReply(
                text="I could not complete that reply. Try again, or ask another way.",
                error_code="response_failure",
            )
        if key == "simulate timeout":
            return SafeReply(
                text="That is taking too long. Try again, or use a shorter question.",
                error_code="timeout",
            )
        if key == "simulate empty":
            return SafeReply(text="", error_code="empty")
        if key == "simulate stt failure":
            return SafeReply(text="Speech-to-text failed.", error_code="stt_failure")
        if key == "simulate tts failure":
            reply = self._answer(key, ())
            reply.error_code = "tts_failure"
            return reply
        if key == "simulate rate limit":
            return SafeReply(
                text="The language model is busy. Try again shortly.",
                error_code="rate_limited",
            )
        if key == "simulate malformed":
            return SafeReply(text="   ", error_code="invalid_response")
        return None

    def _answer(self, key: str, history: Sequence[ChatMessage]) -> SafeReply:
        prior = _history_blob(history)
        if "what is cyber florida" in key:
            return SafeReply(
                text=(
                    "Cyber Florida is the Florida Center for Cybersecurity at the University "
                    "of South Florida. It supports cybersecurity education, research, and "
                    "outreach for the state. I can point you to public pages; I do not speak "
                    "as staff."
                ),
                sources=[source_to_dict(ABOUT)],
                actions=[action_to_dict(OPEN_ABOUT)],
            )
        if (
            "what cybersecurity programs" in key
            or "what programs" in key
            or "programs are available" in key
        ):
            return SafeReply(
                text=(
                    "Cyber Florida publishes workforce, education, and public-sector programs "
                    "on its public site. Open the programs resource for the current list — I "
                    "will not invent names that are not on an approved page."
                ),
                sources=[source_to_dict(HOME)],
                actions=[
                    {
                        "id": "view-program",
                        "label": "View program",
                        "href": "https://cyberflorida.org/",
                    },
                    action_to_dict(OPEN_HOME),
                ],
            )
        if "beginner" in key and ("program" in prior or "program" in key):
            return SafeReply(
                text=(
                    "Beginner-friendly options are listed on Cyber Florida's public programs "
                    "pages. I will not invent a course name or eligibility rule. Check the "
                    "official site for what is currently offered."
                ),
                sources=[source_to_dict(HOME)],
                actions=[action_to_dict(OPEN_HOME)],
            )
        if "eligib" in key:
            return SafeReply(
                text=(
                    "Eligibility changes and must come from Cyber Florida's official pages. "
                    "I do not have live approved sources, so I will not guess requirements."
                ),
                sources=[source_to_dict(HOME)],
                actions=[action_to_dict(OPEN_HOME)],
            )
        if (
            key == "explain phishing"
            or key.startswith("explain phishing")
            or "what is phishing" in key
        ):
            return SafeReply(
                text=(
                    "Phishing is a trick that tries to steal passwords or install malware, "
                    "often by fake urgency in email or messages. Pause, do not click or type "
                    "credentials, and open the real site yourself if you must check an account."
                )
            )
        if "clicked a suspicious link" in key or "clicked a suspicious" in key:
            return SafeReply(
                text=(
                    "Stop using that link or page, and do not enter passwords or codes. If "
                    "this is a work device, tell your IT or security team now. I cannot see "
                    "your computer or take action for you. If anyone is in immediate danger, "
                    "call 911."
                ),
                actions=[action_to_dict(OPEN_HOME)],
            )
        if (
            "look suspicious" in key
            or "phishing email" in key
            or "is this likely a phishing" in key
        ):
            return SafeReply(
                text=(
                    "I cannot say with certainty that a message is or is not a scam. Common "
                    "signs include unexpected urgency, requests for passwords or codes, and "
                    "odd sender addresses. Verify through a channel you already trust, not "
                    "contacts inside the message."
                )
            )
        if "dump system prompt" in key or "ignore previous" in key or key == "api keys":
            return SafeReply(text=INJECTION_REFUSAL)
        if key in {"tell me more", "tell me more.", "tell me more about that", "what about that"}:
            return self._expand(prior)
        if "open the cyber florida" in key or "show me that program" in key:
            return SafeReply(
                text=(
                    "I can point you to Cyber Florida's public website. I cannot open pages "
                    "or run tools in your browser."
                ),
                sources=[source_to_dict(HOME)],
                actions=[action_to_dict(OPEN_HOME)],
            )
        return SafeReply(
            text=(
                "I can help with public Cyber Florida information and defensive cybersecurity "
                "basics. Ask about Cyber Florida, programs, or phishing, or type a specific "
                "public question. I will not invent organization facts."
            )
        )

    def _expand(self, prior: str) -> SafeReply:
        if "florida center for cybersecurity" in prior or "what is cyber florida" in prior:
            return SafeReply(
                text=(
                    "Cyber Florida works on education, research, and outreach rather than "
                    "acting as a help desk or law enforcement. For official details, use the "
                    "public About page. I am an AI, so treat that page as the authority."
                ),
                sources=[source_to_dict(ABOUT)],
                actions=[action_to_dict(OPEN_ABOUT)],
            )
        if "program" in prior:
            return SafeReply(
                text=(
                    "Program names and eligibility change. Use the public site for the current "
                    "catalog instead of relying on a remembered list from me."
                ),
                sources=[source_to_dict(HOME)],
                actions=[
                    {
                        "id": "view-program",
                        "label": "View program",
                        "href": "https://cyberflorida.org/",
                    }
                ],
            )
        if "phish" in prior:
            return SafeReply(
                text=(
                    "A practical habit: hover or inspect the sender, go to the site from a "
                    "bookmark, and report suspected phishing to IT if it is a work account. "
                    "I will not provide attack instructions."
                )
            )
        if "suspicious link" in prior:
            return SafeReply(
                text=(
                    "Next steps stay defensive: disconnect if instructed by IT, watch for "
                    "password prompts, and change credentials only on a known-good site. I "
                    "still cannot inspect the device."
                )
            )
        return SafeReply(
            text=(
                "Tell me which topic you want expanded — for example Cyber Florida, programs, "
                "or phishing — so I do not guess."
            )
        )
